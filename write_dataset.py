import os
import json
import time
import tqdm
import uuid
import requests
import pandas as pd

from typing import List, Dict
from dotenv import load_dotenv



load_dotenv()


BASE_URL = f'http://{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}{os.getenv("API_PREFIX")}'

DATASET_MACHINES = [uuid.uuid4().hex for _ in range(5)]
DATASET_MEASUREMENTS = [uuid.uuid4().hex for _ in range(30)]


class ModelJsonObject(json.JSONEncoder):
	def default(self, obj):
		if hasattr(obj, "__dict__"):
			return {key:value for key, value in obj.__dict__.items() if not key.startswith("_")}
		return super().default(obj)


class VibrationData:
	def __init__(self, x: float, y: float, z: float):
		self.x = x
		self.y = y
		self.z = z
	
	def __repr__(self) -> str:
		return f"x: {self.x}, y: {self.y}, z: {self.z}"


class Measurement:
	def __init__(self, id: str, time: float, data: List[VibrationData] = []):
		self.time = time
		self.id = id
		self.data = data

	def add_new_data(self, new_data: VibrationData):
		self.data.append(new_data)
	
	def add_new_data_list(self, new_data_list: List[VibrationData]):
		self.data.extend(new_data_list)


class Node:
	def __init__(self, node_id:str, measurements: Dict[str, Measurement] = {}):
		self.node_id = node_id
		self.measurements = measurements

	def add_measurement(
		self,
		id: str,
		time: float,
		data: List[VibrationData]
	):
		'''
		If this is a new measurement add it to node and start the timer to check
		sampling, if not, add it to the previously added measurement.
		'''
		if not self.measurements.get(id):
			self.measurements[id] = Measurement(id, time, data)
		else:
			self.measurements[id].add_new_data_list(data)


if __name__ == '__main__':
	df = pd.read_csv('./datasets/accelerometer.csv', usecols=['x', 'y', 'z'])
	datasetLength = 30000
	machinesLength = len(DATASET_MACHINES)
	measurementLength = len(DATASET_MEASUREMENTS)

	baseTime = time.time() - 5 * 60 * 60 * 24

	dList = {}

	for i, row in tqdm.tqdm(df.iterrows()):
		if i == datasetLength - 1:
			break

		machineIndex = int((i / datasetLength) * machinesLength)
		measurementIndex = int(((i % (datasetLength // machinesLength)) / (datasetLength // machinesLength)) * measurementLength)

		vData = VibrationData(x=row['x'], y=row['y'], z=row['z'])

		node_id = DATASET_MACHINES[machineIndex]
		measurement_id = DATASET_MEASUREMENTS[measurementIndex]
  
		if node_id in dList:
			dList[node_id].add_measurement(id=measurement_id, time=baseTime + i, data=[vData])
		else:
			dList[node_id] = Node(node_id=node_id)

	r = requests.post(f'{BASE_URL}/signup/gateway', data=json.dumps({'mac': uuid.uuid4().hex, 'password': 'test'}))
	token = r.json().get('token')
	r.close()

	auth = {'Authorization': f'Bearer {token}'}

	r = requests.post(f'{BASE_URL}/data', data=json.dumps(dList, cls=ModelJsonObject, indent=4), headers=auth)
	print(f'STATUS: {r.status_code}')
	r.close()