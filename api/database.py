import pymssql
from contextlib import contextmanager
from typing import Optional
from config import settings


class DatabaseConnection:
    """Gerenciador de conexão com SQL Server"""

    def __init__(self):
        self.server = settings.DB_SERVER
        self.port = settings.DB_PORT
        self.database = settings.DB_NAME
        self.user = settings.DB_USER
        self.password = settings.DB_PASSWORD

    @contextmanager
    def get_connection(self):
        """Context manager para conexão com o banco"""
        conn = None
        try:
            conn = pymssql.connect(
                server=self.server,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                as_dict=True,
                timeout=60,
                login_timeout=30
            )
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Executa query e retorna resultados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results

    def execute_single(self, query: str, params: Optional[tuple] = None):
        """Executa query e retorna um único resultado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result


class SeniorDatabaseConnection:
    """Gerenciador de conexão com SQL Server Senior (Apenas Leitura)"""

    def __init__(self):
        self.server = settings.SENIOR_DB_SERVER
        self.port = settings.SENIOR_DB_PORT
        self.database = settings.SENIOR_DB_NAME
        self.user = settings.SENIOR_DB_USER
        self.password = settings.SENIOR_DB_PASSWORD

    @contextmanager
    def get_connection(self):
        """Context manager para conexão com o banco Senior"""
        conn = None
        try:
            conn = pymssql.connect(
                server=self.server,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                as_dict=True,
                timeout=120,
                login_timeout=30
            )
            yield conn
        except Exception as e:
            raise Exception(f"Erro ao conectar ao banco Senior: {str(e)}")
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Executa query de leitura e retorna resultados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results


# Instâncias globais
db = DatabaseConnection()  # Banco local (Financeiro)
senior_db = SeniorDatabaseConnection()  # Banco Senior (Sapiens - Leitura)
