import os
import client
from logger import logger


def initial_new_customer_app_database():
    new_user = os.getenv("DB_NEW_USER")
    new_user_password = os.getenv("DB_NEW_USER_PASSWORD")

    psql_client = client.PostgresClient()

    query = f"SELECT 1 FROM pg_database WHERE datname = '{new_user}'"
    db_exists = psql_client.perform_query(query, get_result=True)

    if db_exists is None:
        psql_client.perform_query(f"CREATE DATABASE {new_user}")
        logger.info(f"Database {new_user} created.")
    else:
        logger.info(f"Database {new_user} already exists.")

    query = f"SELECT 1 FROM pg_roles WHERE rolname = '{new_user}'"
    user_exists = psql_client.perform_query(query, get_result=True)

    if user_exists is None:
        query = f"CREATE USER {new_user} WITH PASSWORD '{new_user_password}'"
        psql_client.perform_query(query)

        query = f"GRANT ALL PRIVILEGES ON DATABASE {new_user} TO {new_user}"
        psql_client.perform_query(query)

        logger.info(f"User {new_user} created with all privileges.")
    else:
        logger.info(f"User {new_user} already exists or something went wrong.")


def initial_new_customer_app_dns_records(app_info):
    cf_client = client.CloudflareClient(app_info)
    cf_client.create_dns_record()


if __name__ == "__main__":
    customer_app_info = client.CustomerAppInfo()

    initial_new_customer_app_dns_records(customer_app_info)

    if not customer_app_info.customer_managed:
        initial_new_customer_app_database()
