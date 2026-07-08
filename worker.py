import asyncio
import json
from random import random
import sys
import os

import discord
from redis.asyncio import Redis

from config import WORKERS, REDIS_HOST, REDIS_PORT

# ----------------------------
# Read worker id
# ----------------------------

if len(sys.argv) != 2:
    print("Usage:")
    print("python worker.py <worker_id>")
    exit()

WORKER_ID = int(sys.argv[1])

worker = next(
    (w for w in WORKERS if w["id"] == WORKER_ID),
    None
)

if worker is None:
    print(f"Worker {WORKER_ID} not found.")
    exit()

TOKEN = worker["token"]
VOICE_CHANNEL_ID = worker["voice_channel"]

REDIS_CHANNEL = "tournament"

# ----------------------------
# Redis
# ----------------------------

redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

# ----------------------------
# Discord
# ----------------------------

intents = discord.Intents.default()


class WorkerBot(discord.Client):

    def __init__(self):
        super().__init__(intents=intents)

        self.voice_client = None
        self.audio_queue = asyncio.Queue()

        self.redis_task = None
        self.player_task = None

    async def on_ready(self):

        print("=" * 40)
        print(f"Worker #{WORKER_ID} Ready")
        print("=" * 40)
        print(self.user)
        print("Connected to Discord")

        try:
            await redis.ping()
            print("Connected to Redis")

        except Exception as e:
            print("Redis Error:", e)

        print("Waiting for commands...")
        print("=" * 40)

        if self.redis_task is None or self.redis_task.done():
            self.redis_task = asyncio.create_task(self.redis_listener())

        if self.player_task is None or self.player_task.done():
            self.player_task = asyncio.create_task(self.audio_player())

    # ----------------------------

    async def join_voice(self):

        if self.voice_client and self.voice_client.is_connected():
            print("Already connected.")
            return

        channel = self.get_channel(VOICE_CHANNEL_ID)

        if channel is None:
            print("Voice channel not found.")
            return

        try:

            self.voice_client = await channel.connect()

            print(f"Joined {channel.name}")

        except Exception as e:

            print("Join Error:", e)

    # ----------------------------

    async def leave_voice(self):

        if not self.voice_client:

            print("Not connected.")

            return

        try:
            await asyncio.sleep(random.uniform(0.3, 1.0))  # Random delay between 0.3 and 1 second
            await self.voice_client.disconnect()

            self.voice_client = None

            print("Disconnected.")

        except Exception as e:

            print("Leave Error:", e)

    # ----------------------------

    async def redis_listener(self):

        pubsub = redis.pubsub()

        await pubsub.subscribe(REDIS_CHANNEL)

        async for message in pubsub.listen():

            if message["type"] != "message":
                continue

            try:

                data = json.loads(message["data"])

            except Exception:

                continue

            target = data["target"]

            if target != "all" and target != WORKER_ID:
                continue

            action = data["action"]

            print()
            print("Received:", data)

            if action == "join":

                await self.join_voice()

            elif action == "leave":

                await self.leave_voice()

            elif action == "announce":

                event = data["event"]

                await self.audio_queue.put(event)
    
        
    async def audio_player(self):

        while True:

            event = await self.audio_queue.get()

            try:

                audio_file = f"audios/{event}.mp3"

                if not os.path.exists(audio_file):
                    print(f"{audio_file} missing")
                    continue

                if self.voice_client is None:
                    print("Not connected")
                    continue

                finished = asyncio.Event()

                source = discord.FFmpegPCMAudio(audio_file)

                self.voice_client.play(
                    source,
                    after=lambda e: finished.set()
                )

                print(f"Playing {audio_file}")

                await finished.wait()

            finally:

                self.audio_queue.task_done()



bot = WorkerBot()

try:

    bot.run(TOKEN)

except KeyboardInterrupt:

    print("Stopped.")

finally:

    asyncio.run(redis.close())