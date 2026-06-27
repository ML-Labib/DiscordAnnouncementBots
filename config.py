import os
from dotenv import load_dotenv
load_dotenv()

# Access the variables
MASTER_TOKEN = os.getenv("MASTER_TOKEN")
WORKER_01_TOKEN = os.getenv("WORKER_01_TOKEN")
WORKER_02_TOKEN = os.getenv("WORKER_02_TOKEN")
WORKER_03_TOKEN = os.getenv("WORKER_03_TOKEN")



REDIS_HOST = "localhost"
REDIS_PORT = 6379

WORKERS = [
    {
        "id": 1,
        "token": WORKER_01_TOKEN,
        "voice_channel": 1431861918905143379
    },
    {
        "id": 2,
        "token": WORKER_02_TOKEN,
        "voice_channel": 1449811379753189507
    },
    {
        "id": 3,
        "token": WORKER_03_TOKEN,
        "voice_channel": 1449811424326193336
    }
]