import json
import asyncio
import random
import discord
from discord import app_commands
from redis.asyncio import Redis
from config import MASTER_TOKEN
# ===========================
# CONFIG
# ===========================



REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Worker IDs
WORKER_IDS = list(range(1, 17))

REDIS_CHANNEL = "tournament"

# ===========================
# REDIS
# ===========================

redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

# ===========================
# BOT
# ===========================

intents = discord.Intents.default()


class MasterBot(discord.Client):

    def __init__(self):
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):

        print("=" * 40)
        print(" Tournament Master Ready")
        print("=" * 40)
        print(f"Logged in as {self.user}")
        print()

        try:
            pong = await redis.ping()

            if pong:
                print("Redis Connected")

        except Exception as e:
            print("Redis Error:", e)

        print("Slash Commands Synced")
        print("=" * 40)


bot = MasterBot()


# ==========================================================
# Helper
# ==========================================================

async def publish(action, target, event=None):

    payload = {
        "action": action,
        "target": target
    }

    if event:
        payload["event"] = event

    try:

        await redis.publish(
            REDIS_CHANNEL,
            json.dumps(payload)
        )

        return True

    except Exception as e:

        print("Redis Publish Error:", e)

        return False


def valid_target(target: str):

    if target.lower() == "all":
        return "all"

    try:

        worker = int(target)

        if worker not in WORKER_IDS:
            return None

        return worker

    except:
        return None


# ==========================================================
# /join
# ==========================================================
@bot.tree.command(name="join", description="Tell worker(s) to join voice channel.")
@app_commands.describe(target="all or worker number (1-16)")
async def join(interaction: discord.Interaction, target: str):

    worker = valid_target(target)

    if worker is None:
        await interaction.response.send_message(
            "❌ Invalid worker.\nUse **all** or **1-16**.",
            ephemeral=True
        )
        return

    success = await publish("join", worker)

    if success:
        await interaction.response.send_message(
            f"✅ Join command sent to **{worker}**"
        )
    else:
        await interaction.response.send_message(
            "❌ Redis publish failed."
        )
# ==========================================================
# /leave
# ==========================================================

@bot.tree.command(
    name="leave",
    description="Tell worker(s) to leave voice channel."
)

@app_commands.describe(
    target="all or worker number (1-16)"
)

async def leave(

        interaction: discord.Interaction,
        target: str
):

    worker = valid_target(target)

    if worker is None:

        await interaction.response.send_message(
            "❌ Invalid worker.",
            ephemeral=True
        )
        return

    success = await publish(
        "leave",
        worker
    )

    if success:

        await interaction.response.send_message(
            f"✅ Leave command sent to **{worker}**"
        )

    else:

        await interaction.response.send_message(
            "❌ Redis publish failed."
        )


# ==========================================================
# /announce
# ==========================================================

@bot.tree.command(
    name="announce",
    description="Play announcement."
)

@app_commands.describe(
    event="welcome / thanks / match1 ...",
    target="all or worker number"
)

async def announce(

        interaction: discord.Interaction,
        event: str,
        target: str
):

    worker = valid_target(target)

    if worker is None:

        await interaction.response.send_message(
            "❌ Invalid worker.",
            ephemeral=True
        )
        return

    success = await publish(
        "announce",
        worker,
        event
    )

    if success:

        await interaction.response.send_message(
            f"📢 Announcement **{event}** sent to **{worker}**"
        )

    else:

        await interaction.response.send_message(
            "❌ Redis publish failed."
        )

# helper function
async def join_all_workers():
    print("Joining all workers...")

    for worker_id in WORKER_IDS:
        success = await publish("join", worker_id)

        if success:
            print(f"Join sent to Worker {worker_id}")
        else:
            print(f"Failed to send join to Worker {worker_id}")

        await asyncio.sleep(random.uniform(0.3, 0.5))

    print("Finished sending join commands.")


# ==========================================================
# Run
# ==========================================================

try:
    bot.run(MASTER_TOKEN)

except KeyboardInterrupt:
    print("Master Bot Stopped.")

finally:

    asyncio.run(redis.close())