"""
Serviço de autenticação e autorização
Responsável por gerenciar login, JWT tokens, 2FA e permissões
"""

import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from passlib.context import CryptContext
from jose import JWTError, jwt
from config import settings

logger = logging.getLogger(__name__)

# Configuração do contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
SECRET_KEY = getattr(settings, 'JWT_SECRET_KEY', 'your-secret-key-here-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 dias


class AuthService:
    """Serviço para operações de autenticação e autorização"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash bcrypt de uma senha

        Args:
            password: Senha em texto plano

        Returns:
            Hash bcrypt da senha
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha corresponde ao hash

        Args:
            plain_password: Senha em texto plano
            hashed_password: Hash bcrypt da senha

        Returns:
            True se a senha está correta, False caso contrário
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Cria um token JWT de acesso

        Args:
            data: Dados a serem codificados no token
            expires_delta: Tempo de expiração customizado (opcional)

        Returns:
            Token JWT codificado
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Cria um token JWT de refresh

        Args:
            data: Dados a serem codificados no token

        Returns:
            Token JWT de refresh codificado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
        """
        Verifica e decodifica um token JWT

        Args:
            token: Token JWT a ser verificado
            token_type: Tipo do token ("access" ou "refresh")

        Returns:
            Payload do token se válido, None caso contrário
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Verifica se é o tipo correto de token
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch. Expected {token_type}, got {payload.get('type')}")
                return None

            return payload

        except JWTError as e:
            logger.error(f"Erro ao verificar token: {e}")
            return None

    @staticmethod
    def generate_2fa_code() -> str:
        """
        Gera um código de 6 dígitos para 2FA

        Returns:
            Código de 6 dígitos
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    @staticmethod
    def get_2fa_expiry() -> datetime:
        """
        Retorna o tempo de expiração para código 2FA (5 minutos)

        Returns:
            Datetime de expiração
        """
        return datetime.utcnow() + timedelta(minutes=5)

    @staticmethod
    def is_2fa_expired(expires_at: Optional[datetime]) -> bool:
        """
        Verifica se o código 2FA expirou

        Args:
            expires_at: Data/hora de expiração

        Returns:
            True se expirou ou não existe, False caso contrário
        """
        if not expires_at:
            return True
        return datetime.utcnow() > expires_at

    @staticmethod
    def is_2fa_blocked(blocked_until: Optional[datetime]) -> bool:
        """
        Verifica se o usuário está bloqueado para tentativas 2FA

        Args:
            blocked_until: Data/hora até quando está bloqueado

        Returns:
            True se bloqueado, False caso contrário
        """
        if not blocked_until:
            return False
        return datetime.utcnow() < blocked_until

    @staticmethod
    def get_2fa_block_time(attempts: int) -> Optional[datetime]:
        """
        Calcula tempo de bloqueio baseado no número de tentativas

        Args:
            attempts: Número de tentativas falhas

        Returns:
            Datetime até quando bloquear, ou None se não deve bloquear
        """
        if attempts >= 5:
            # Bloqueia por 30 minutos após 5 tentativas
            return datetime.utcnow() + timedelta(minutes=30)
        return None

    @staticmethod
    def check_permission(user_role_id: int, required_role_level: int) -> bool:
        """
        Verifica se o usuário tem permissão baseado no nível da role
        Quanto MENOR o nível, MAIOR o poder (0 = Super Admin)

        Args:
            user_role_id: ID da role do usuário (0, 1, 2, 3)
            required_role_level: Nível mínimo necessário

        Returns:
            True se tem permissão, False caso contrário
        """
        # role_id e level são iguais no nosso caso (0=Super Admin, 1=Admin, 2=Gestor, 3=Usuário)
        return user_role_id <= required_role_level

    @staticmethod
    def is_super_admin(user_role_id: int) -> bool:
        """
        Verifica se o usuário é Super Admin

        Args:
            user_role_id: ID da role do usuário

        Returns:
            True se é Super Admin, False caso contrário
        """
        return user_role_id == 0

    @staticmethod
    def create_token_pair(user_data: dict) -> Tuple[str, str]:
        """
        Cria um par de tokens (access e refresh) para o usuário

        Args:
            user_data: Dados do usuário (id, email, role_id, client_id)

        Returns:
            Tupla (access_token, refresh_token)
        """
        token_data = {
            "sub": str(user_data.get("id")),
            "email": user_data.get("email"),
            "role_id": user_data.get("role_id"),
            "client_id": str(user_data.get("client_id")) if user_data.get("client_id") else None
        }

        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)

        return access_token, refresh_token
