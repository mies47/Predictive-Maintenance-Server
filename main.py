import os
import uvicorn
from dotenv import load_dotenv
from app import initialize_server

app = initialize_server()

load_dotenv()

SERVER_STR = os.getenv('SERVER_STR')
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = int(os.getenv('SERVER_PORT'))


if __name__ == '__main__':
    uvicorn.run(SERVER_STR, host=SERVER_HOST, port=SERVER_PORT, reload=True)