import os
import io
import json
import logging
import boto3
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

# Kapcsolatok beállítása
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}")

s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
    aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
    aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    region_name='us-east-1'
)
BUCKET_NAME = "landing-zone"

def load_csv_to_pg(date_str):
    """CSV fájl beolvasása MinIO-ból és feltöltése Postgres-be."""
    object_name = f"csv/orders/{date_str}/orders.csv"
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_name)
        df = pd.read_csv(response.get("Body"))

        df.to_sql('raw_orders', engine, schema='public', if_exists='append', index=False)
        logging.info(f"[OK] {len(df)} rendelés betöltve a Postgres-be.")
    except Exception as e:
        logging.error(f"Hiba a CSV betöltésekor: {e}")

def load_json_to_pg(date_str, folder, table_name):
    """JSON fájl beolvasása MinIO-ból és feltöltése Postgres-be."""
    object_name = f"api/{folder}/{date_str}/{folder}.json"
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_name)
        json_data = json.loads(response.get("Body").read().decode('utf-8'))

        records = json_data.get('data', [])
        df = pd.DataFrame(records)

        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, dict)).any():
                df[col] = df[col].apply(json.dumps)

        if_exists_rule = 'replace' if folder == 'products' else 'append'
        df.to_sql(table_name, engine, schema='public', if_exists=if_exists_rule, index=False)
        logging.info(f"[OK] {len(df)} {folder} betöltve a {table_name} táblába.")
    except Exception as e:
        logging.error(f"Hiba a JSON betöltésekor ({folder}): {e}")

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    logging.info(f"--- Postgres betöltés indítása ({today}) ---")

    load_csv_to_pg(today)
    load_json_to_pg(today, "products", "raw_products")
    load_json_to_pg(today, "reviews", "raw_reviews")