import os
import psycopg2
import requests

from logger import logger
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from settings import UAD_DOMAIN, CF_API_URL


class CloudflareClient:
    def __init__(self, api_key="thisisaapikey", api_email="anemail@email.com"):
        self.api_email = os.getenv("CF_API_EMAIL") or api_email
        self.api_key = os.getenv("CF_API_KEY") or api_key
        self.default_header = {
            "Content-Type": "application/json",
            "X-Auth-Key": self.api_key,
            "X-Auth-Email": self.api_email
        }
    
    def _get_zone_identifiers(self):
        url = f"{CF_API_URL}/zones"
        response = requests.request("GET", url, headers=self.default_header)
        zone_ids = [result["id"] for result in response.json()["result"] if result["name"] == UAD_DOMAIN]
        return zone_ids

    def create_dns_record(self):
        zone_ids = self._get_zone_identifiers()

        for zone_id in zone_ids:
            url = f"{CF_API_URL}/zones/{zone_id}/dns_records"

            backend_payload = {
                "content": UAD_DOMAIN,
                "name": f"api-{os.getenv('CF_CUSTOMER_APP_CNAME_RECORD')}",
                "proxied": True,
                "type": "CNAME",
                "ttl": 1
            }

            frontend_payload = {
                "content": UAD_DOMAIN,
                "name": os.getenv("CF_CUSTOMER_APP_CNAME_RECORD"),
                "proxied": True,
                "type": "CNAME",
                "ttl": 1
            }

            logger.info(f"Adding subdomain {os.getenv('CF_CUSTOMER_APP_CNAME_RECORD')}")
            response = requests.request("POST", url, json=frontend_payload, headers=self.default_header)
            logger.info(response.json())

            response = requests.request("POST", url, json=backend_payload, headers=self.default_header)
            logger.info(f"Add subdomain api-{os.getenv('CF_CUSTOMER_APP_CNAME_RECORD')}")
            logger.info(response.json())


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

    def perform_query(self, query, get_result=False):
        self.connector.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with self.connector.cursor() as cursor:
            logger.info(f"Running query: {query}")
            cursor.execute(query)
            if get_result:
                return cursor.fetchone()
