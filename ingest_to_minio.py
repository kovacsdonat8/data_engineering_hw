# ingest_to_minio.py
import os
import json
import logging
import requests
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = "landing-zone"

s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name='us-east-1'
)

def create_bucket_if_not_exists(bucket_name):
    """Létrehozza a MinIO bucketet, ha még nem létezik."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logging.info(f"A(z) '{bucket_name}' bucket már létezik.")
    except ClientError:
        logging.info(f"A(z) '{bucket_name}' bucket létrehozása...")
        s3_client.create_bucket(Bucket=bucket_name)

def upload_to_minio(data, object_name, is_json=False):
    """Feltölti az adatot a MinIO-ba."""
    try:
        if is_json:
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=object_name,
                Body=json.dumps(data),
                ContentType='application/json'
            )
        else:
            s3_client.upload_file(data, BUCKET_NAME, object_name)
        logging.info(f"Sikeres feltöltés: {object_name}")
    except Exception as e:
        logging.error(f"Hiba a feltöltés során ({object_name}): {e}")

def ingest_api_data(date_str):
    """API végpontok hívása és az adatok MinIO-ba mentése."""
    api_base_url = "http://localhost:8000/api"

    try:
        prod_resp = requests.get(f"{api_base_url}/products")
        prod_resp.raise_for_status()
        upload_to_minio(
            data=prod_resp.json(),
            object_name=f"api/products/{date_str}/products.json",
            is_json=True
        )
    except Exception as e:
        logging.error(f"Hiba a termékek lekérésekor: {e}")

    try:
        rev_resp = requests.get(f"{api_base_url}/reviews", params={"date": date_str})
        rev_resp.raise_for_status()
        upload_to_minio(
            data=rev_resp.json(),
            object_name=f"api/reviews/{date_str}/reviews.json",
            is_json=True
        )
    except Exception as e:
        logging.error(f"Hiba az értékelések lekérésekor: {e}")

def ingest_csv_data(date_str):
    """Generált CSV fájl feltöltése a MinIO-ba."""
    file_path = f"mock_data/output/orders_{date_str}.csv"
    if os.path.exists(file_path):
        upload_to_minio(
            data=file_path,
            object_name=f"csv/orders/{date_str}/orders.csv",
            is_json=False
        )
    else:
        logging.warning(f"Nem található a CSV fájl: {file_path}")

if __name__ == "__main__":
    create_bucket_if_not_exists(BUCKET_NAME)

    today = datetime.now().strftime("%Y-%m-%d")
    logging.info(f"--- Ingestion indítása a(z) {today} dátumra ---")

    ingest_api_data(today)
    ingest_csv_data(today)

    logging.info("--- Ingestion befejezve ---")