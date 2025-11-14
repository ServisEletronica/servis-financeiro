from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import traceback
import pymssql

from services.auth_service import AuthService
from database import get_db_connection

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


# ========== MODELS (Request/Response) ==========

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Login2FARequest(BaseModel):
    email: EmailStr
    code: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    requires_2fa: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[dict] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    full_name: str
    role_id: int
    role_name: str
    client_id: Optional[str]
    is_active: bool


# ========== FUNÇÕES AUXILIARES ==========

def get_user_by_email(email: str):
    """Busca usuário por email no banco"""
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        query = """
        SELECT
            u.id,
            u.email,
            u.password_hash,
            u.first_name,
            u.full_name,
            u.role_id,
            r.name as role_name,
            u.client_id,
            u.is_active,
            u.whatsapp,
            u.whatsapp_verified,
            u.two_factor_enabled,
            u.two_factor_code,
            u.two_factor_expires_at,
            u.two_factor_attempts,
            u.two_factor_blocked_until
        FROM dbo.users u
        INNER JOIN dbo.user_roles r ON u.role_id = r.id
        WHERE u.email = %s
        """
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        conn.close()


def update_user_2fa(user_id: str, code: str, expires_at: datetime):
    """Atualiza código 2FA do usuário"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        UPDATE dbo.users
        SET two_factor_code = %s,
            two_factor_expires_at = %s,
            two_factor_attempts = 0
        WHERE id = %s
        """
        cursor.execute(query, (code, expires_at, user_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def increment_2fa_attempts(user_id: str) -> int:
    """Incrementa tentativas 2FA e retorna o novo valor"""
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Incrementa tentativas
        query_update = """
        UPDATE dbo.users
        SET two_factor_attempts = two_factor_attempts + 1
        WHERE id = %s
        """
        cursor.execute(query_update, (user_id,))
        conn.commit()

        # Busca o novo valor
        query_select = "SELECT two_factor_attempts FROM dbo.users WHERE id = %s"
        cursor.execute(query_select, (user_id,))
        result = cursor.fetchone()

        attempts = result['two_factor_attempts'] if result else 0

        # Se atingiu 5 tentativas, bloqueia
        if attempts >= 5:
            block_until = AuthService.get_2fa_block_time(attempts)
            query_block = """
            UPDATE dbo.users
            SET two_factor_blocked_until = %s
            WHERE id = %s
            """
            cursor.execute(query_block, (block_until, user_id))
            conn.commit()

        return attempts
    finally:
        cursor.close()
        conn.close()


def clear_2fa_data(user_id: str):
    """Limpa dados 2FA após login bem-sucedido"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        UPDATE dbo.users
        SET two_factor_code = NULL,
            two_factor_expires_at = NULL,
            two_factor_attempts = 0,
            two_factor_blocked_until = NULL,
            last_login_at = SYSUTCDATETIME()
        WHERE id = %s
        """
        cursor.execute(query, (user_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ========== ROTAS ==========

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Primeiro passo do login: valida credenciais e envia código 2FA
    """
    try:
        # Busca usuário
        user = get_user_by_email(request.email)

        if not user:
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")

        # Verifica se usuário está ativo
        if not user['is_active']:
            raise HTTPException(status_code=403, detail="Usuário inativo")

        # Verifica senha
        if not AuthService.verify_password(request.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")

        # Se 2FA não está habilitado, faz login direto
        if not user['two_factor_enabled']:
            user_data = {
                "id": str(user['id']),
                "email": user['email'],
                "role_id": user['role_id'],
                "client_id": str(user['client_id']) if user['client_id'] else None
            }

            access_token, refresh_token = AuthService.create_token_pair(user_data)

            clear_2fa_data(str(user['id']))

            return LoginResponse(
                requires_2fa=False,
                message="Login realizado com sucesso",
                access_token=access_token,
                refresh_token=refresh_token,
                user={
                    "id": str(user['id']),
                    "email": user['email'],
                    "first_name": user['first_name'],
                    "full_name": user['full_name'],
                    "role_id": user['role_id'],
                    "role_name": user['role_name'],
                    "client_id": str(user['client_id']) if user['client_id'] else None
                }
            )

        # Gera e envia código 2FA
        code = AuthService.generate_2fa_code()
        expires_at = AuthService.get_2fa_expiry()

        update_user_2fa(str(user['id']), code, expires_at)

        # TODO: Enviar código via WhatsApp (integração futura)
        print(f"[DEBUG] Código 2FA para {user['email']}: {code}")

        return LoginResponse(
            requires_2fa=True,
            message=f"Código de verificação enviado para {user['whatsapp'] or 'seu WhatsApp'}"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro no login: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro ao realizar login")


@router.post("/verify-2fa", response_model=TokenResponse)
async def verify_2fa(request: Login2FARequest):
    """
    Segundo passo do login: valida código 2FA e retorna tokens
    """
    try:
        # Busca usuário
        user = get_user_by_email(request.email)

        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")

        # Verifica se está bloqueado
        if AuthService.is_2fa_blocked(user['two_factor_blocked_until']):
            raise HTTPException(
                status_code=429,
                detail="Muitas tentativas. Tente novamente em 30 minutos"
            )

        # Verifica se código expirou
        if AuthService.is_2fa_expired(user['two_factor_expires_at']):
            raise HTTPException(status_code=401, detail="Código expirado. Faça login novamente")

        # Verifica código
        if user['two_factor_code'] != request.code:
            attempts = increment_2fa_attempts(str(user['id']))
            remaining = 5 - attempts

            if remaining <= 0:
                raise HTTPException(
                    status_code=429,
                    detail="Muitas tentativas incorretas. Conta bloqueada por 30 minutos"
                )

            raise HTTPException(
                status_code=401,
                detail=f"Código incorreto. Tentativas restantes: {remaining}"
            )

        # Código correto - gera tokens
        user_data = {
            "id": str(user['id']),
            "email": user['email'],
            "role_id": user['role_id'],
            "client_id": str(user['client_id']) if user['client_id'] else None
        }

        access_token, refresh_token = AuthService.create_token_pair(user_data)

        # Limpa dados 2FA
        clear_2fa_data(str(user['id']))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao verificar 2FA: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro ao verificar código")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Renova o access token usando o refresh token
    """
    try:
        # Verifica refresh token
        payload = AuthService.verify_token(request.refresh_token, token_type="refresh")

        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")

        # Cria novo par de tokens
        user_data = {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "role_id": payload.get("role_id"),
            "client_id": payload.get("client_id")
        }

        access_token, refresh_token = AuthService.create_token_pair(user_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao renovar token: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro ao renovar token")


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Retorna dados do usuário atual baseado no token
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token não fornecido")

        token = authorization.replace("Bearer ", "")
        payload = AuthService.verify_token(token, token_type="access")

        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")

        # Busca dados atualizados do usuário
        user = get_user_by_email(payload.get("email"))

        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if not user['is_active']:
            raise HTTPException(status_code=403, detail="Usuário inativo")

        return UserResponse(
            id=str(user['id']),
            email=user['email'],
            first_name=user['first_name'],
            full_name=user['full_name'],
            role_id=user['role_id'],
            role_name=user['role_name'],
            client_id=str(user['client_id']) if user['client_id'] else None,
            is_active=user['is_active']
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao buscar usuário: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro ao buscar dados do usuário")
