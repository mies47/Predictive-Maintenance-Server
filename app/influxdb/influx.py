import json
from datetime import datetime
from collections import defaultdict
from typing import Dict

from ..models.SendDataModel import NodeModel
from ..utils.env_vars import INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, INFLUXDB_URI
from ..utils.constants import PROCESSED_DATA_EXPIRATION_TIME

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDB:
    MAIN_TABLES = ['vibration_measurment']
    ALL_TABLES = MAIN_TABLES.extend(['psd_feature', 'rms_feature', 'harmonic_peaks'])

    def __init__(self):
        self.client = InfluxDBClient(url=INFLUXDB_URI, org=INFLUXDB_ORG, token=INFLUXDB_TOKEN)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()


    def write_vibration_data(self, data: Dict[str, NodeModel]):
        points = []
        
        for nodeId, nodeModel in data.items():

            for measurementId, measurement in nodeModel.measurements.items():
                for i, vibrationData in enumerate(measurement.data):
                    
                    x_point = Point('vibration_measurement')\
                        .tag('nodeId', nodeId)\
                            .tag('measurementId', measurementId)\
                                .tag('index', i)\
                                    .field('x', vibrationData.x)\
                                        .time(time=datetime.utcfromtimestamp(measurement.time))
                
                    y_point = Point('vibration_measurement')\
                        .tag('nodeId', nodeId)\
                            .tag('measurementId', measurementId)\
                                .tag('index', i)\
                                    .field('y', vibrationData.y)\
                                        .time(time=datetime.utcfromtimestamp(measurement.time))
                    
                    z_point = Point('vibration_measurement')\
                        .tag('nodeId', nodeId)\
                            .tag('measurementId', measurementId)\
                                .tag('index', i)\
                                    .field('z', vibrationData.z)\
                                        .time(time=datetime.utcfromtimestamp(measurement.time))
                    
                    points.extend([x_point, y_point, z_point])

        self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)


    def get_vibration_data(self, nodeId: str = None):
        '''Returns all vibration data written in db if nodeId is None'''

        filter_by_node = f'|> filter(fn:(r) => r.nodeId == "{nodeId}")'
        query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: 0)\
        |> filter(fn:(r) => r._measurement == "vibration_measurement")\
        {filter_by_node if nodeId is not None else ""}\
        |> keep(columns: ["_time", "_field", "_value", "nodeId", "measurementId", "index"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> yield()'

        query_result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        query_result = json.loads(query_result.to_json(orient='records'))

        results = defaultdict(lambda: defaultdict(lambda: []))
        for r in query_result:
            print(r)
            results[r['nodeId']][r['measurementId']].append({
                'x': r['x'],
                'y': r['y'],
                'z': r['z'],
                'time': r['_time'] // 1000
            })

        return results
    

    def get_all_nodes_id(self):
        query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: 0)\
        |> filter(fn:(r) => r._measurement == "vibration_measurement")\
        |> keep(columns: ["_time", "_field", "_value", "nodeId"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> distinct(column: "nodeId")'

        query_result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        query_result = json.loads(query_result.to_json(orient='records'))

        results = [r['nodeId'] for r in query_result]

        return results


    def get_all_measurements_id(self, nodeId: str = None):
        filter_by_node = f'|> filter(fn:(r) => r.nodeId == "{nodeId}")'

        query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: 0)\
        |> filter(fn:(r) => r._measurement == "vibration_measurement")\
        {filter_by_node if nodeId is not None else ""}\
        |> keep(columns: ["_time", "_field", "_value", "measurementId"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> distinct(column: "measurementId")'

        query_result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        query_result = json.loads(query_result.to_json(orient='records'))

        results = [r['measurementId'] for r in query_result]

        return results
    
    
    def write_rms_features(self, rms_features: defaultdict(lambda: defaultdict(lambda: {}))):
        points = []

        for nId, measurements in rms_features.items():
            for mId, rms in measurements.items():
                insertion_time = datetime.utcnow()

                x_point = Point('rms_feature')\
                                .tag('nodeId', nId)\
                                    .tag('measurementId', mId)\
                                        .field('x_rms_value', rms['x'])\
                                            .time(time=insertion_time)

                y_point = Point('rms_feature')\
                                .tag('nodeId', nId)\
                                    .tag('measurementId', mId)\
                                        .field('y_rms_value', rms['y'])\
                                            .time(time=insertion_time)
                                            
                z_point = Point('rms_feature')\
                                .tag('nodeId', nId)\
                                    .tag('measurementId', mId)\
                                        .field('z_rms_value', rms['z'])\
                                            .time(time=insertion_time)
                                            
                points.extend([x_point, y_point, z_point])
                    
        self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)


    def get_rms_features(self, nodeId = None, measurmentId = None):
        filter_by_node = f'|> filter(fn:(r) => r.nodeId == "{nodeId}")'
        filter_by_measurment = f'|> filter(fn:(r) => r.measurmentId == "{measurmentId}")'

        query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: {-1 * PROCESSED_DATA_EXPIRATION_TIME}m)\
        |> filter(fn:(r) => r._measurement == "rms_feature")\
        {filter_by_node if nodeId is not None else ""}\
        {filter_by_measurment if measurmentId is not None else ""}\
        |> keep(columns: ["_time", "_field", "_value", "nodeId", "measurementId"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> yield()'

        query_result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        query_result = json.loads(query_result.to_json(orient='records'))

        results = defaultdict(lambda: defaultdict(lambda: {}))
        for r in query_result:
            print(r)
            results[r['nodeId']][r['measurementId']] = {
                'x': r['x_rms_value'],
                'y': r['y_rms_value'],
                'z': r['z_rms_value']
            }

        return results
    

    def write_psd_features(self, psd_features: defaultdict(lambda: defaultdict(lambda: []))):
        points = []

        for nId, measurements in psd_features.items():
            for mId, psd in measurements.items():
                for i, feature in enumerate(psd):
                    points.append(Point('psd_feature')\
                                    .tag('nodeId', nId)\
                                        .tag('measurementId', mId)\
                                            .tag('frequency', feature['frequency'])\
                                                .tag('index', i)\
                                                    .field('psd_value', feature['psd_value'])\
                                                        .time(time=datetime.utcnow()))
                    
        self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)


    def get_psd_features(self, nodeId = None, measurmentId = None):
        filter_by_node = f'|> filter(fn:(r) => r.nodeId == "{nodeId}")'
        filter_by_measurment = f'|> filter(fn:(r) => r.measurmentId == "{measurmentId}")'

        query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: {-1 * PROCESSED_DATA_EXPIRATION_TIME}m)\
        |> filter(fn:(r) => r._measurement == "psd_feature")\
        {filter_by_node if nodeId is not None else ""}\
        {filter_by_measurment if measurmentId is not None else ""}\
        |> keep(columns: ["_time", "_field", "_value", "nodeId", "measurementId", "frequency", "index"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> yield()'

        query_result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        query_result = json.loads(query_result.to_json(orient='records'))

        results = defaultdict(lambda: defaultdict(lambda: []))
        for r in query_result:
            results[r['nodeId']][r['measurementId']].append({
                'psd_value': r['psd_value'],
                'frequency': r['frequency']
            })

        return results
    
    
    def write_harmonic_peaks(self, harmonic_peaks: defaultdict(lambda: defaultdict(lambda: []))):
        points = []

        for nId, measurements in harmonic_peaks.items():
            for mId, psd in measurements.items():
                for i, feature in enumerate(psd):
                    points.append(Point('harmonic_peaks')\
                                    .tag('nodeId', nId)\
                                        .tag('measurementId', mId)\
                                            .tag('frequency', feature['frequency'])\
                                                .tag('index', i)\
                                                    .field('psd_value', feature['psd_value'])\
                                                        .time(time=datetime.utcnow()))
                    
        self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)


    def get_harmonic_peaks(self, nodeId = None, measurmentId = None):
        filter_by_node = f'|> filter(fn:(r) => r.nodeId == "{nodeId}")'
        filter_by_measurment = f'|> filter(fn:(r) => r.measurmentId == "{measurmentId}")'

        query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: {-1 * PROCESSED_DATA_EXPIRATION_TIME}m)\
        |> filter(fn:(r) => r._measurement == "harmonic_peaks")\
        {filter_by_node if nodeId is not None else ""}\
        {filter_by_measurment if measurmentId is not None else ""}\
        |> keep(columns: ["_time", "_field", "_value", "nodeId", "measurementId", "frequency", "index"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> yield()'

        query_result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        query_result = json.loads(query_result.to_json(orient='records'))

        results = defaultdict(lambda: defaultdict(lambda: []))
        for r in query_result:
            results[r['nodeId']][r['measurementId']].append({
                'harmonic_peaks': r['harmonic_peaks'],
                'frequency': r['frequency']
            })

        return results
    
    
    def clear_cached_data(self):
        import datetime

        delete_api = self.client.delete_api()
        
        for table in InfluxDB.ALL_TABLES:
            if table not in InfluxDB.MAIN_TABLES:
                delete_api.delete(start='1970-01-01T00:00:00Z', stop=datetime.datetime.now(), predicate=f'_measurement="{table}"', bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG)
        

    
    def clear_database(self):
        import datetime

        delete_api = self.client.delete_api()
        
        for table in InfluxDB.ALL_TABLES:
            delete_api.delete(start='1970-01-01T00:00:00Z', stop=datetime.datetime.now(), predicate=f'_measurement="{table}"', bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG)