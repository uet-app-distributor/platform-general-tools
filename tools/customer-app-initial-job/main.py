import os
import client


def initial_new_customer_app_database():
    new_user = os.getenv("DB_NEW_USER")
    new_user_password = os.getenv("DB_NEW_USER_PASSWORD")

    psql_client = client.PostgresClient()

    psql_client.perform_query(f"CREATE DATABASE {new_user}")
    psql_client.perform_query(f"CREATE USER {new_user} WITH PASSWORD '{new_user_password}'")
    psql_client.perform_query(f"GRANT ALL PRIVILEGES ON DATABASE {new_user} TO {new_user}")


def initial_new_customer_app_dns_records():
    cf_client = client.CloudflareClient()
    cf_client.create_dns_record()


if __name__ == "__main__":
    # initial_new_customer_app_database()
    initial_new_customer_app_dns_records()
