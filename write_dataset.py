import os
import json
import time
import tqdm
import uuid
import random
import pandas as pd

from dotenv import load_dotenv
from datetime import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


load_dotenv()


DATASET_MACHINES = [uuid.uuid4().hex for _ in range(4)]
DATASET_MEASUREMENTS = [uuid.uuid4().hex for _ in range(10)]

INFLUXDB_HOST = os.getenv('INFLUXDB_HOST')
INFLUXDB_PORT = os.getenv('INFLUXDB_PORT')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')

INFLUXDB_URI = f'http://{INFLUXDB_HOST}:{INFLUXDB_PORT}'.replace(' ', '%20')


if __name__ == '__main__':
    df = pd.read_csv('./datasets/accelerometer.csv', usecols=['x', 'y', 'z'])
    datasetLength = 10000
    
    machinesLength = len(DATASET_MACHINES)
    measurementLength = len(DATASET_MEASUREMENTS)
    
    t1 = int(time.time() - 20 * 60 * 60 * 24)
    t2 = int(time.time())
    
    points = []
    
    print('***READING DATASET***')
    
    for i, row in tqdm.tqdm(df.iterrows()):
        if i == datasetLength - 1:
            break
        
        machineIndex = int((i / datasetLength) * machinesLength)
        measurementIndex = int(((i % (datasetLength // machinesLength)) / (datasetLength // machinesLength)) * measurementLength)
        
        nodeId = DATASET_MACHINES[machineIndex]
        measurementId = DATASET_MEASUREMENTS[measurementIndex]
        
        new_point = Point('vibration_measurement')\
                        .tag('nodeId', nodeId)\
                            .tag('measurementId', measurementId)\
                                .tag('index', i)\
                                    .field('x', row['x'])\
                                        .field('y', row['y'])\
                                            .field('z', row['z'])\
                                                .time(time=datetime.utcfromtimestamp(random.randint(t1, t2)))
                                                
        points.append(new_point)
        
    print('***CONNECTING TO DATABASE***')
    
    client = InfluxDBClient(url=INFLUXDB_URI, org=INFLUXDB_ORG, token=INFLUXDB_TOKEN)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    print('***WRITING DATASET***')
    
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
    
    print('DONE')