import json
from datetime import datetime
from collections import defaultdict

from ..models.SendDataModel import VibrationDataModel
from ..utils.env_vars import INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, INFLUXDB_URI

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDB:

    def __init__(self):
        self.client = InfluxDBClient(url=INFLUXDB_URI, org=INFLUXDB_ORG, token=INFLUXDB_TOKEN)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()


    def write_vibration_data(self,nodeId: str, data: VibrationDataModel):
        x_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .tag('measurementId', data.measurementId)\
                    .field('x', data.x)\
                        .time(time=datetime.utcfromtimestamp(data.time))
        
        y_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .tag('measurementId', data.measurementId)\
                    .field('y', data.y)\
                        .time(time=datetime.utcfromtimestamp(data.time))
        
        z_point = Point('vibration_measurement')\
            .tag('nodeId', nodeId)\
                .tag('measurementId', data.measurementId)\
                    .field('z', data.z)\
                        .time(time=datetime.utcfromtimestamp(data.time))

        self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=[x_point, y_point, z_point])


    '''Returns all vibration data written in db if nodeId is None'''
    def get_vibration_data(self, nodeId: str = None):
        filter_by_node = f'|> filter(fn:(r) => r.nodeId == "{nodeId}")'
        query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: 0)\
        |> filter(fn:(r) => r._measurement == "vibration_measurement")\
        {filter_by_node if nodeId is not None else ""}\
        |> keep(columns: ["_time", "_field", "_value", "nodeId", "measurementId"])\
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
        |> yield()'

        result = self.query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
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