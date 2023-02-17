import os
from dotenv import load_dotenv

from influxdb_client import InfluxDBClient

load_dotenv()

DB_HOST = os.getenv('INFLUXDB_HOST')
DB_PORT = os.getenv('INFLUXDB_PORT')
DB_ORG = os.getenv('INFLUXDB_ORG')
DB_BUCKET = os.getenv('INFLUXDB_BUCKET')
DB_TOKEN = os.getenv('INFLUXDB_TOKEN')

URL = f'http://{DB_HOST}:{DB_PORT}'

client = InfluxDBClient(url=URL, org=DB_ORG, token=DB_TOKEN)

print(client.health())