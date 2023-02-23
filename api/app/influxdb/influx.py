import os
import json
import copy
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict

from ..models.SendDataModel import VibrationDataModel

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

import numpy as np

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


    def write_vibration_data(self, measurementId: str, nodeId: str, data: VibrationDataModel):
        x_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .tag('measurementId', measurementId)\
                    .field('x', data.x)\
                        .time(time=datetime.utcfromtimestamp(data.time))
        
        y_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .tag('measurementId', measurementId)\
                    .field('y', data.y)\
                        .time(time=datetime.utcfromtimestamp(data.time))
        
        z_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .tag('measurementId', measurementId)\
                    .field('z', data.z)\
                        .time(time=datetime.utcfromtimestamp(data.time))

        self.write_api.write(bucket=DB_BUCKET, org=DB_ORG, record=[x_point, y_point, z_point])


    '''Returns all vibration data written in db if nodeId is None'''
    def get_vibration_data(self, nodeId: str = None):
        filter_by_node = f'|> filter(fn:(r) => r.nodeId == "{nodeId}")'
        query = f'from(bucket:"{DB_BUCKET}")\
        |> range(start: 0)\
        |> filter(fn:(r) => r._measurement == "vibration_measurement")\
        {filter_by_node if nodeId is not None else ""}\
        |> keep(columns: ["_time", "_field", "_value", "nodeId", "measurementId"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> yield()'

        result = self.query_api.query_data_frame(org=DB_ORG, query=query)
        result = json.loads(result.to_json(orient='records'))

        results = defaultdict(lambda: defaultdict(lambda: []))
        for r in result:
            results[r['nodeId']][r['measurementId']].append({
                'x': r['x'],
                'y': r['y'],
                'z': r['z'],
                'time': r['_time']
            })

        return results


    def _create_matrices(self, data):
        matrices = copy.deepcopy(data)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                matrices[nId][mId] = [np.array([sample['x'], sample['y'], sample['z']], dtype=np.float32) for sample in m]

        return matrices


    def _normalize_vibration_data(self, matrices):
        normalized_matrices = copy.deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                sum_of_samples = np.add.reduce(m)
                normalized_matrices[nId][mId] = np.array(m)

                # Subtracting the average sum of samples from the collected samples
                if len(m) > 1:
                    normalized_matrices[nId][mId] -= sum_of_samples / len(m)

        return normalized_matrices


    def preprocess_vibration_data(self, nodeId: str = None):
        # Fetching the data from database
        data = self.get_vibration_data(nodeId=nodeId)

        # Creating matrices from raw data
        matrices = self._create_matrices(data=data)

        # Normalizing samples to remove gravity effect
        normalized_data = self._normalize_vibration_data(matrices=matrices)

        print(normalized_data)
        