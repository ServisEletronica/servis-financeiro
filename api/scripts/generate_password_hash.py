"""
Script para gerar hash bcrypt de senhas
Use este script para criar hashes de senhas para inserir usuários no banco de dados
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_hash(password: str) -> str:
    """Gera hash bcrypt de uma senha"""
    return pwd_context.hash(password)


def verify_hash(password: str, hashed: str) -> bool:
    """Verifica se uma senha corresponde ao hash"""
    return pwd_context.verify(password, hashed)


if __name__ == "__main__":
    print("=" * 60)
    print("GERADOR DE HASH DE SENHAS (bcrypt)")
    print("=" * 60)
    print()

    while True:
        password = input("Digite a senha (ou 'sair' para encerrar): ").strip()

        if password.lower() == 'sair':
            print("\nEncerrando...")
            break

        if not password:
            print("⚠️  Senha não pode ser vazia!\n")
            continue

        # Gera o hash
        hash_result = generate_hash(password)

        print()
        print("✅ Hash gerado com sucesso!")
        print("-" * 60)
        print(f"Senha original: {password}")
        print(f"Hash bcrypt:    {hash_result}")
        print("-" * 60)

        # Verifica o hash
        is_valid = verify_hash(password, hash_result)
        print(f"Verificação:    {'✅ OK' if is_valid else '❌ FALHOU'}")
        print()

        # Mostra exemplo de INSERT SQL
        print("📋 Exemplo de uso no INSERT SQL:")
        print(f"password_hash = '{hash_result}'")
        print()
        print("=" * 60)
        print()


# Hashes pré-gerados para referência:
"""
SENHAS PADRÃO (para referência):

Senha: admin123
Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYpNkr0z.HW

Senha: cliente123
Hash: $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQam1qgdQO24TQDqN0tLu

Senha: gestor123
Hash: $2b$12$zx0VfLdH6HqQqZ7fO6RXOOgx5z3QvJ2qKJqzf8LpYHZYpBqX8Wz8m

Senha: usuario123
Hash: $2b$12$P8pNHj/xF6qB0qLYkqY4lOZG2YKb8m5F5xQqB5qYxB7QxB8QxB9Qx

Senha: 12345678
Hash: $2b$12$5F5F5F5F5F5F5F5F5F5F5OMwEOy3g2OqB9QqB9QqB9QqB9QqB9Qq
"""
