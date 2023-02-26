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


    def _create_matrices(self, data: defaultdict(lambda: defaultdict(lambda: []))):
        matrices = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

        for nId, measurements in data.items():
            for mId, m in measurements.items():
                for sample in m:
                    matrices[nId][mId]['x'].append(sample['x'])
                    matrices[nId][mId]['y'].append(sample['y'])
                    matrices[nId][mId]['z'].append(sample['z'])
                
                # Converting collected smaples to numpy arrays
                matrices[nId][mId]['x'] = np.array(matrices[nId][mId]['x'], dtype=np.float32)
                matrices[nId][mId]['y'] = np.array(matrices[nId][mId]['y'], dtype=np.float32)
                matrices[nId][mId]['z'] = np.array(matrices[nId][mId]['z'], dtype=np.float32)

        return matrices


    def _normalize_vibration_data(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        normalized_matrices = copy.deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]
                sum_of_x_samples = np.sum(m['x'])
                sum_of_y_samples = np.sum(m['y'])
                sum_of_z_samples = np.sum(m['z'])

                # Subtracting the average sum of samples from the collected samples
                if number_of_samples > 1:
                    normalized_matrices[nId][mId]['x'] -= sum_of_x_samples / number_of_samples
                    normalized_matrices[nId][mId]['y'] -= sum_of_y_samples / number_of_samples
                    normalized_matrices[nId][mId]['z'] -= sum_of_z_samples / number_of_samples

        return normalized_matrices

    
    def _rms_feature_extraction(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        rms_feature = copy.deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]
                l2_norm_of_x_samples = np.linalg.norm(m['x'])
                l2_norm_of_y_samples = np.linalg.norm(m['y'])
                l2_norm_of_z_samples = np.linalg.norm(m['z'])

                rms_feature[nId][mId] = (l2_norm_of_x_samples / np.sqrt(number_of_samples)) ** 2 \
                    + (l2_norm_of_y_samples / np.sqrt(number_of_samples)) ** 2 \
                        + (l2_norm_of_z_samples / np.sqrt(number_of_samples)) ** 2

        return rms_feature


    def preprocess_vibration_data(self, nodeId: str = None):
        # Fetching the data from database
        data = self.get_vibration_data(nodeId=nodeId)

        # Creating matrices from raw data
        matrices = self._create_matrices(data=data)

        # Normalizing samples to remove gravity effect
        normalized_data = self._normalize_vibration_data(matrices=matrices)

        # Extracting RMS (Root Mean Square) feature from normalized data
        rms_feature = self._rms_feature_extraction(matrices=normalized_data)