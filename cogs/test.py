import discord, pymongo, motor, json, time, random, math, asyncio
import motor.motor_asyncio
from discord.ext import commands

with open("config.json") as f:
    config = json.load(f)

client = motor.motor_asyncio.AsyncIOMotorClient(config["DB_URI"])
db = client["peak"]
userdb = db["users"]
serverdb = db["servers"]

class test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def add_server(self, ctx):
        if (await serverdb.find_one({"_id": ctx.guild.id})) is None:
            await serverdb.insert_one(
                    {
                        "_id": ctx.guild.id, 
                        "users": {
                            ctx.author.id: {
                                "xp": 0, 
                                "level": 0, 
                                "coins": 0,
                                "messages": {
                                    f"{time.time()}": {
                                        "title": "Welcome to Peak!",
                                        "description": "Welcome to Peak! We hope you enjoy your stay!",
                                        "color": "00ff00",
                                        "timestamp": time.time()
                                    }
                                },
                                "created_at": time.time()
                            }
                        },
                        "created_at": ctx.guild.created_at,
                        "premium": False
                    }
            )
            return True
        else:
            return False
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Listens for when a member joins a guild and sends a message to the system channel.

        Args:
            member (discord.Member): The member who joined the guild.
        """
        # Send a message to the system channel when a member joins
        channel = member.guild.system_channel
        if member.guild.id == 1238555988538167306:
            if channel is not None:
                await channel.send(f'aye my nigga {member.mention} just joined whats up')

    @commands.Cog.listener()
    async def on_guild_booster_add(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'holy shit {member.mention} just boosted the server!\nWe now have {member.guild.premium_subscription_count} boosters!')


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Listens for when a member leaves a guild and sends a message to the system channel.

        Args:
            member (discord.Member): The member who left the guild.
        """
        # Send a message to the system channel when a member leaves
        if member.guild.id == 1238555988538167306:
            channel = member.guild.system_channel
            if channel is not None:
                await channel.send(f'aye my nigga **{member.name}** just left wtf bro.. u my opp..')

    @commands.command()
    async def test(self, ctx):
        await ctx.send('Test command successfully executed.')

    @commands.command()
    @commands.is_owner()
    async def test2(self, ctx):
        if (await serverdb.find_one({"_id": ctx.guild.id})) is None:
            await serverdb.insert_one(
                    {
                        "_id": ctx.guild.id, 
                        "users": {
                            f"{ctx.author.id}": {
                                "xp": 0, 
                                "level": 0, 
                                "coins": 0,
                                "messages": {
                                    f"{time.time()}": {
                                        "title": "Welcome to Peak!",
                                        "description": "Welcome to Peak! We hope you enjoy your stay!",
                                        "color": "00ff00",
                                        "timestamp": time.time()
                                    }
                                },
                                "created_at": time.time()
                            }
                        },
                        "created_at": ctx.guild.created_at,
                        "premium": False
                    }
            )
            return True
        else:
            return False

    @commands.command()
    async def srank(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        svdata = await serverdb.find_one({"_id": ctx.guild.id})
        if svdata is None:
            await self.add_server(ctx)
        memdata = await serverdb.find_one({"_id": member.id, "users": {f"{member.id}": {"$exists": True}}})
        xp = memdata['xp']
        level = memdata['level']
        await ctx.send(f"{member.mention} is level {level} with {xp} xp")
        

def setup(bot):
    bot.add_cog(test(bot))


