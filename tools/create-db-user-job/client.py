import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from logger import logger


class PostgresClient:
    def __init__(self):
        self.db_password = os.getenv("DB_PASSWORD") or "postgres"
        self.db_host = os.getenv("DB_HOST") or "localhost"
        self.db_port = os.getenv("DB_PORT") or 5432
        self.db_user = os.getenv("DB_USER") or "postgres"
        self.db_name = os.getenv("DB_NAME") or "postgres"

        self.connector = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )

    def perform_query(self, query):
        self.connector.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with self.connector.cursor() as cursor:
            logger.info(f"Running query: {query}")
            cursor.execute(query)
