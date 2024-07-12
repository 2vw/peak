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

async def add_user(ctx, server):
    if (await serverdb.find_one({"_id": f"{server.id}"})):
        if ctx.id in (await serverdb.find_one({"_id": f"{server.id}"}))["data"]["users"]:
            return True
        else:
            serverdb.update_one(
                {"_id": f"{server.id}"},
                {"$set": {"data.users": {f"{ctx.id}": {"xp": 0, "multiplier": 1, "banned": False, "created_at": f"{time.time()}", "moderation": {"warns": {}, "notes": {}}}}}}
            )
            return True
    else:
        await add_server(ctx)

class database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author.bot:
            return
        elif (await serverdb.find_one({"_id": f"{message.guild.id}"})):
            if f"{message.author.id}" in (await serverdb.find_one({"_id": f"{message.guild.id}"}))["data"]["users"]:
                pass
            else:
                await add_user(message.author, message.guild)
        else:
            await add_server(message)
    
    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        if (await serverdb.find_one({"_id": f"{member.guild.id}"})):
            if f"{member.id}" in (await serverdb.find_one({"_id": f"{member.guild.id}"}))["data"]["users"]:
                pass
            else:
                await add_user(member, member.guild)
        else:
            await add_server(member)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        if (await serverdb.find_one({"_id": f"{member.guild.id}"})):
            if f"{member.id}" in (await serverdb.find_one({"_id": f"{member.guild.id}"}))["data"]["users"]:
                await serverdb.delete_one({"_id": f"{member.guild.id}", "data.users": {f"{member.id}": {"$exists": True}}})

    @commands.command(name="prefix", description="Get the prefix list for this server.")
    async def prefix_(self, ctx):
        prefixes = (await serverdb.find_one({"_id": f"{ctx.guild.id}"}))["data"]["settings"]["prefix"]
        embed = discord.Embed(title="Prefixes", description="\n".join(prefixes), color=ctx.author.color)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def settings(self, ctx):
        await ctx.send_help(ctx.command)

    @settings.group(name="prefix", description="Set, add, and edit prefixes.", invoke_without_command=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
        

    @prefix.command(name="set", description="Set the prefix for the server. (CLEARS EVERYTHING!)")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_(self, ctx, *, prefix):
        if prefix is None:
            example_prefix = (await serverdb.find_one({"_id": f"{ctx.guild.id}"}))["data"]["settings"]["prefix"][0]
            return await ctx.send(embed=discord.Embed(description=f"Example command: `{ctx.prefix}prefix set {example_prefix}`"))
        msg = await ctx.send(embed=discord.Embed(description=f"Are you sure you want to set the prefix to `{prefix}` for this server? It will clear **every** other prefix in this server! (yes/no)"))
        confirm = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.content.lower() in ['yes', 'no'])
        if confirm.content.lower() == 'no':
            await ctx.send("Command cancelled.")
            return
        serverdb.update_one(
            {"_id": f"{ctx.guild.id}"},
            {"$set": {"data.settings.prefix": [prefix]}}
        )
        await ctx.send(embed=discord.Embed(description=f"Set prefix `{prefix}` for this server. Use `{prefix}prefix` to view your new list."))
    
    @prefix.command(name="add", description="Add another prefix for the server.")
    @commands.has_guild_permissions(manage_guild=True)
    async def add_(self, ctx, *, prefix):
        if prefix is None:
            example_prefix = (await serverdb.find_one({"_id": f"{ctx.guild.id}"}))["data"]["settings"]["prefix"][0]
            return await ctx.send(embed=discord.Embed(description=f"Example command: `{ctx.prefix}prefix add {example_prefix}`"))
        elif prefix in (await serverdb.find_one({"_id": f"{ctx.guild.id}"}))["data"]["settings"]["prefix"]:
            embed = discord.Embed(description=f"That prefix is already in the list.", color=0xff0000)
            return await ctx.send(embed=embed)
        serverdb.update_one(
            {"_id": f"{ctx.guild.id}"},
            {"$push": {"data.settings.prefix": prefix}}
        )
        await ctx.send(embed=discord.Embed(description=f"Added prefix `{prefix}` to this servers list. Use `{prefix}prefix` to view."))
    
    @prefix.command(name="remove", description="Remove a prefix from the server.")
    @commands.has_guild_permissions(manage_guild=True)
    async def remove_(self, ctx, *, prefix):
        if prefix is None:
            example_prefix = (await serverdb.find_one({"_id": f"{ctx.guild.id}"}))["data"]["settings"]["prefix"][0]
            return await ctx.send(embed=discord.Embed(description=f"Example command: `{ctx.prefix}prefix remove {example_prefix}`"))
        try:
            serverdb.update_one(
                {"_id": f"{ctx.guild.id}"},
                {"$pull": {"data.settings.prefix": prefix}}
            )
            await ctx.send(embed=discord.Embed(description=f"Removed prefix `{prefix}` from this servers list. Use `{(await serverdb.find_one({'_id': f'{ctx.guild.id}'}))['data']['settings']['prefix'][0]}prefix` to view."))
        except:
            await ctx.send(embed=discord.Embed(description=f"Prefix `{prefix}` not found in this servers list. Use `{ctx.prefix}prefix` to view."))
def setup(bot):
    bot.add_cog(database(bot))


