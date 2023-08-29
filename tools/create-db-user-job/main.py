import os
import client


if __name__ == "__main__":
    new_user = os.getenv("DB_NEW_USER")
    new_user_password = os.getenv("DB_NEW_USER_PASSWORD")

    psql_client = client.PostgresClient()
    psql_client.perform_query(
        f"CREATE USER {new_user} WITH PASSWORD '{new_user_password}'"
    )
