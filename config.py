import os
from dotenv import load_dotenv
load_dotenv()

# Access the variables
MASTER_TOKEN = os.getenv("MASTER_TOKEN")
WORKER_01_TOKEN = os.getenv("WORKER_01_TOKEN")
WORKER_02_TOKEN = os.getenv("WORKER_02_TOKEN")
WORKER_03_TOKEN = os.getenv("WORKER_03_TOKEN")
WORKER_04_TOKEN = os.getenv("WORKER_04_TOKEN")
WORKER_05_TOKEN = os.getenv("WORKER_05_TOKEN")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
OPERATOR_ROLE = "Support Staff"
COMMAND_CHANNEL_ID = 1523935069494972517 #BD_Extreme server's #command channel id
WORKERS = [
    {
        "id": 1,
        "token": WORKER_01_TOKEN,
        "voice_channel": 1464018655267393537
    },
    {
        "id": 2,
        "token": WORKER_02_TOKEN,
        "voice_channel": 1473567577753124884
    },
    {
        "id": 3,
        "token": WORKER_03_TOKEN,
        "voice_channel": 1473567674289356840
    },
    {
        "id": 4,
        "token": WORKER_04_TOKEN,
        "voice_channel": 1473568103379238945
    },
    {
        "id": 5,
        "token": WORKER_05_TOKEN,
        "voice_channel": 1473568140737904772
    }
]