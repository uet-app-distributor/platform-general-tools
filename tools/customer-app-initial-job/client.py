import os
import psycopg2
import requests

from logger import logger
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from settings import UAD_DOMAIN, CF_API_URL


class CustomerAppInfo:
    def __init__(self, customer_name="sample-customer", customer_app="sample-webapp"):
        self.customer_name = os.getenv("CUSTOMER_NAME") or customer_name
        self.customer_app = os.getenv("CUSTOMER_APP") or customer_app
        self.app_id = f"{self.customer_name}-{self.customer_app}"
        self.customer_managed = os.getenv("CUSTOMER_MANAGED") == "true"


class CloudflareClient:
    def __init__(
        self, app_info, api_key="thisisaapikey", api_email="anemail@email.com"
    ):
        self.app_info = app_info
        self.api_email = os.getenv("CF_API_EMAIL") or api_email
        self.api_key = os.getenv("CF_API_KEY") or api_key
        self.default_header = {
            "Content-Type": "application/json",
            "X-Auth-Key": self.api_key,
            "X-Auth-Email": self.api_email,
        }

    def _get_zone_identifiers(self):
        url = f"{CF_API_URL}/zones"
        response = requests.request("GET", url, headers=self.default_header)
        zone_ids = [
            result["id"]
            for result in response.json()["result"]
            if result["name"] == UAD_DOMAIN
        ]
        return zone_ids

    def create_dns_record(self):
        zone_ids = self._get_zone_identifiers()

        for zone_id in zone_ids:
            url = f"{CF_API_URL}/zones/{zone_id}/dns_records"

            if not self.app_info.customer_managed:
                frontend_payload = {
                    "content": UAD_DOMAIN,
                    "name": os.getenv("CF_CUSTOMER_APP_CNAME_RECORD"),
                    "proxied": True,
                    "type": "CNAME",
                    "ttl": 1,
                }

                backend_payload = {
                    "content": UAD_DOMAIN,
                    "name": f"api-{os.getenv('CF_CUSTOMER_APP_CNAME_RECORD')}",
                    "proxied": True,
                    "type": "CNAME",
                    "ttl": 1,
                }
            else:
                frontend_payload = {
                    "content": os.getenv("CUSTOMER_INSTANCE_PUBLIC_IP"),
                    "name": f"{self.app_info.app_id}.{UAD_DOMAIN}",
                    "proxied": True,
                    "type": "A",
                    "ttl": 1,
                }

                backend_payload = {
                    "content": os.getenv("CUSTOMER_INSTANCE_PUBLIC_IP"),
                    "name": f"api-{self.app_info.app_id}.{UAD_DOMAIN}",
                    "proxied": True,
                    "type": "A",
                    "ttl": 1,
                }

            self._make_dns_request(url, frontend_payload)
            self._make_dns_request(url, backend_payload)

    def _make_dns_request(self, url, payload):
        response = requests.request(
            "POST", url, json=payload, headers=self.default_header
        )
        logger.info(f"Added {payload['name']} subdomain ...")
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
