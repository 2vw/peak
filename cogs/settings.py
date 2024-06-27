import discord, pymongo, motor, json, time, random, math, asyncio
import motor.motor_asyncio
from discord.ext import commands

with open("config.json") as f:
    config = json.load(f)

client = motor.motor_asyncio.AsyncIOMotorClient(config["DB_URI"])
db = client["peak"]
userdb = db["users"]
serverdb = db["servers"]

async def add_server(ctx):
    if (await serverdb.find_one({"_id": f"{ctx.guild.id}"})):
        return True
    else:
        serverdb.insert_one({
            "_id": f"{ctx.guild.id}",
            "logged": time.time(),
            "mod": {
                "log": False,
                "welcome": False,
                "leave": False,
                "invite": False,
                "ban": False,
                "kick": False,
                "purge": False,
                "warn": False,
                "message": False,
                "command": False
            },
            "data": {
                "settings": {
                    "prefix": ["p!", "p?", "p.", "P!", "P?", "P."],
                    "premium": False,
                    "react": {
                        "enabled": False,
                        'y/n': {
                            "triggers": ["y/n", "yes/no", "y/n", "yes/no"],
                            "enabled": False,
                            "emojis": ["✅", "❌"]
                        },
                        'heart': {
                            "triggers": ["heart", "hearts", "<3"],
                            "enabled": False,
                            "emojis": ["❤"]
                        },
                        'star': {
                            "triggers": ["star", "stars"],
                            "enabled": False,
                            "emojis": ["⭐"]
                        }
                    }
                },
                "users": {
                    f"{ctx.author.id}": {
                        "xp": 0,
                        "multiplier": 1,
                        "banned": False,
                        "created_at": time.time(),
                        "moderation": {
                            "warns": {},
                            "notes": {}
                        },
                        "messages": {
                            f"{time.time()}": {
                                "title": "Welcome to Peak!",
                                "description": "Welcome to Peak! We hope you enjoy your stay!",
                                "color": "00ff00",
                                "timestamp": time.time()
                            }
                        }
                    }
                }
            }
        })

async def add_user(ctx):
    if ctx.server.id in serverdb.find_one({"_id": f"{ctx.server.id}"}):
        if ctx.author.id in (await serverdb.find_one({"_id": f"{ctx.server.id}"}))["data"]["users"]:
            return True
        else:
            serverdb.update_one(
                {"_id": ctx.server.id},
                {"$set": {"data.users": {f"{ctx.author.id}": {"xp": 0, "multiplier": 1, "banned": False, "created_at": f"{time.time()}", "moderation": {"warns": {}, "notes": {}}}}}}
            )
            return True
    else:
        await add_server(ctx)

class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author.bot:
            return
        elif (await serverdb.find_one({"_id": f"{message.guild.id}"})):
            if f"{message.author.id}" in (await serverdb.find_one({"_id": f"{message.guild.id}"}))["data"]["users"]:
                print("user exists")
            else:
                await add_user(message)
                print(f"added user {message.author.name}")
        else:
            await add_server(message)
            print(f"added server {message.guild.name}")
    

def setup(bot):
    bot.add_cog(settings(bot))


