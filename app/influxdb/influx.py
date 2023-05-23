import json
from datetime import datetime
from collections import defaultdict
from typing import Dict

from ..models.SendDataModel import NodeModel
from ..utils.env_vars import INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, INFLUXDB_URI

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDB:

    def __init__(self):
        self.client = InfluxDBClient(url=INFLUXDB_URI, org=INFLUXDB_ORG, token=INFLUXDB_TOKEN)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()


    def write_vibration_data(self, data: Dict[str, NodeModel]):
        points = []
        
        for nodeId, nodeModel in data.items():

            for measurementId, measurement in nodeModel.measurements.items():
                for vibrationData in measurement.data:

                    x_point = Point('vibration_measurement')\
                        .tag('nodeId', nodeId)\
                            .tag('measurementId', measurementId)\
                                .field('x', vibrationData.x)\
                                    .time(time=datetime.utcfromtimestamp(measurement.time))
                
                    y_point = Point('vibration_measurement')\
                        .tag('nodeId', nodeId)\
                            .tag('measurementId', measurementId)\
                                .field('y', vibrationData.y)\
                                    .time(time=datetime.utcfromtimestamp(measurement.time))
                    
                    z_point = Point('vibration_measurement')\
                        .tag('nodeId', nodeId)\
                            .tag('measurementId', measurementId)\
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
        |> keep(columns: ["_time", "_field", "_value", "nodeId", "measurementId"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> yield()'

        query_result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        query_result = json.loads(query_result.to_json(orient='records'))

        results = defaultdict(lambda: defaultdict(lambda: []))
        for r in query_result:
            results[r['nodeId']][r['measurementId']].append({
                'x': r['x'],
                'y': r['y'],
                'z': r['z'],
                'time': r['_time']
            })

        return results
    

    def get_all_nodes_id(self):
        query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: 0)\
        |> filter(fn:(r) => r._measurement == "vibration_measurement")\
        |> keep(columns: ["nodeId"])\
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
        |> keep(columns: ["measurementId"])\
        |> distinct(column: "measurementId")'

        query_result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        query_result = json.loads(query_result.to_json(orient='records'))

        results = [r['measurementId'] for r in query_result]

        return results

    
    def clear_database(self):
        import datetime

        delete_api = self.client.delete_api()
        delete_api.delete(start='1970-01-01T00:00:00Z', stop=datetime.datetime.now(), predicate='_measurement="vibration_measurement"', bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG)