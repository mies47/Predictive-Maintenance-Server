import os
import json
import uuid
import requests
import pandas as pd
from typing import List
from dotenv import load_dotenv
from tqdm import tqdm


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
	def __init__(self, time: float, measurementId: str, x: float, y: float, z: float):
		self.time = time
		self.measurementId = measurementId
		self.x = x
		self.y = y
		self.z = z


class DataModel:
	def __init__(self, nodeId: str, vibrationData: List[VibrationData] = []):
		self.nodeId = nodeId
		self.vibrationData = vibrationData


	def add_vibration_data(self, d: VibrationData):
		self.vibrationData.append(d)


class DataModelList:
	def __init__(self, data: List[DataModel] = []):
		self.data = data


	def add_data_model(self, d: DataModel):
		self.data.append(d)


	def get_node_data_model(self, nodeId: str) -> DataModel:
		for dataModel in self.data:
			if dataModel.nodeId == nodeId:
				return dataModel
		dataModel = DataModel(nodeId=nodeId)
		self.add_data_model(d=dataModel)

		return dataModel


	def add_vibration_data(self, nodeId: str, vibrationData: VibrationData):
		for i, dataModel in enumerate(self.data):
			if dataModel.nodeId == nodeId:
				self.data[i].add_vibration_data(d=vibrationData)
				return
		
		dataModel = DataModel(nodeId=nodeId, vibrationData=[vibrationData])
		self.add_data_model(d=dataModel)


if __name__ == '__main__':
	df = pd.read_csv('./datasets/accelerometer.csv', usecols=['x', 'y', 'z'])
	datasetLength = 50000
	machinesLength = len(DATASET_MACHINES)
	measurementLength = len(DATASET_MEASUREMENTS)

	baseTime = 1622193008

	dataModelList = DataModelList()

	for i, row in tqdm(df.iterrows()):
		if i == datasetLength - 1:
			break

		machineIndex = int((i / datasetLength) * machinesLength)
		measurementIndex = int(((i % (datasetLength // machinesLength)) / (datasetLength // machinesLength)) * measurementLength)

		vData = VibrationData(time=baseTime + i, measurementId=DATASET_MEASUREMENTS[measurementIndex], x=row['x'], y=row['y'], z=row['z'])

		dataModelList.add_vibration_data(nodeId=DATASET_MACHINES[machineIndex], vibrationData=vData)

	r = requests.post(f'{BASE_URL}/signup/gateway', data=json.dumps({'mac': uuid.uuid4().hex, 'password': 'test'}))
	token = r.json().get('token')
	r.close()

	auth = {'Authorization': f'Bearer {token}'}

	r = requests.post(f'{BASE_URL}/data', data=json.dumps(dataModelList, cls=ModelJsonObject, indent=4), headers=auth)
	r.close()