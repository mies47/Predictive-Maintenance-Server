import os
from datetime import datetime
from dotenv import load_dotenv

from ..models.SendDataModel import VibrationDataModel

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

DB_HOST = os.getenv('INFLUXDB_HOST')
DB_PORT = os.getenv('INFLUXDB_PORT')
DB_ORG = os.getenv('INFLUXDB_ORG')
DB_BUCKET = os.getenv('INFLUXDB_BUCKET')
DB_TOKEN = os.getenv('INFLUXDB_TOKEN')

URL = f'http://{DB_HOST}:{DB_PORT}'


class InfluxDB:

    def __init__(self):
        self.client = InfluxDBClient(url=URL, org=DB_ORG, token=DB_TOKEN)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()


    def write_vibration_data(self, nodeId: str, data: VibrationDataModel):
        x_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .field('x', data.x)\
                    .time(time=datetime.utcfromtimestamp(data.time))
        
        y_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .field('y', data.y)\
                    .time(time=datetime.utcfromtimestamp(data.time))
        
        z_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .field('z', data.z)\
                    .time(time=datetime.utcfromtimestamp(data.time))

        self.write_api.write(bucket=DB_BUCKET, org=DB_ORG, record=[x_point, y_point, z_point])
    

    def get_all_vibration_data(self):
        query = f'from(bucket:"{DB_BUCKET}") |> range(start: 0)'

        result = self.query_api.query(org=DB_ORG, query=query)

        for table in result:
            for record in table.records:
                print(record)


    def get_node_vibration_data(self, nodeId: str):
        query = f'from(bucket:"{DB_BUCKET}")\
        |> filter(fn:(r) => r._measurement == "vibration_measurement")\
        |> filter(fn:(r) => r.nodeId == "{nodeId}")'

        result = self.query_api.query(org=DB_ORG, query=query)
