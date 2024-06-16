import discord, pymongo, motor, json, time, random, math, asyncio
import motor.motor_asyncio
from discord.ext import commands

with open("config.json") as f:
    config = json.load(f)

client = motor.motor_asyncio.AsyncIOMotorClient(config["DB_URI"])
db = client["peak"]
userdb = db["users"]
serverdb = db["servers"]


class leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def add_user(self, member):
        if member.bot:
            return
        if (await userdb.find_one({"_id": member.id})) is None:
            await userdb.insert_one(
                    {
                        "_id": member.id, 
                        "xp": 0, 
                        "level": 0, 
                        "coins": 0, 
                        "messages": {
                            f"{time.time()}": {
                                "title": "Welcome to Peak!",
                                "description": "Welcome to Peak! We hope you enjoy your stay!",
                                "color": "00ff00",
                                "timestamp": round(time.time())
                            }
                        },
                        "created_at": round(time.time())
                        }
                    )
            return True
        else:
            return False

    async def reset_all(self, ctx):
        i = 0
        for user in await userdb.find({}).to_list(length=1000):
            i += 1
            await userdb.delete_one({"_id": user["_id"]})
        await ctx.send("Cleared all data for all (" + str(i) + ") users!")

    async def add_all(self, ctx):
        i = 0
        for member in ctx.guild.members:
            if not userdb.find_one({"_id": member.id}) and not member.bot:
                i += 1
                await self.add_user(member)
        await ctx.reply(f"Added all ({len(ctx.guild.members)}) users!\nSkipped over {len(ctx.guild.members) - i} bots / pre-registered users!")
                

    async def update_xp(self, member):
        if (await userdb.find_one({"_id": member.id})) is None:
            await self.add_user(member)
        else:
            await userdb.update_one(
                {"_id": member.id},
                {"$inc": {"xp": 1}}
            )
            if time.time() % 120 > 100:
                await userdb.update_one(
                    {"_id": member.id},
                    {"$inc": {"xp": random.randint(10, 50)}}
                )
            # Create a very complex equation that requires increasingly high amounts of xp to get to the next level
            # This equation is x^1000 + 5x - 20
            # We multiply the xp by 10 to make it easier to adjust the rate of leveling up
            memdata = await userdb.find_one({"_id": member.id})
            xp = int((memdata['xp'] * 10) ** 1000 + 5 * (memdata['xp'] * 10) - 20)
            level = int((memdata['level'] * 100) ** 1000 + 5 * (memdata['level'] * 100) - 20)
            if xp >= level:
                await userdb.update_one(
                    {"_id": member.id},
                    {"$set": {"level": memdata['level'] + 1}}
                )
            elif xp < level - 1000:
                await userdb.update_one(
                    {"_id": member.id},
                    {"$set": {"level": memdata['level'] - 1}}
                )
            return True
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_xp(member)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if (await userdb.find_one({"_id": message.author.id})) is None:
            await self.add_user(message.author)
            print(f"Created user {message.author.display_name} in {message.guild.name} ({message.guild.id})")
        else:
            await self.update_xp(message.author)
        
    @commands.command(name="level", usage="`[member]`", aliases=["lvl", 'xp', 'rank'])
    async def level(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        elif (await userdb.find_one({"_id": member.id})) is None:
            await self.add_user(member)
            return await ctx.send("User not found! Please try again!")
        level = await userdb.find_one({"_id": member.id})
        embed = discord.Embed(title=f"{member.display_name}'s XP", color=discord.Color.green())
        embed.add_field(name="XP", value=level["xp"])
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        leaderboard = []
        async for user in userdb.find({}):
            leaderboard.append((user["_id"], user["xp"]))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        for i, user in enumerate(leaderboard):
            if user[0] == member.id:
                embed.set_footer(text=f"Leaderboard Position: {i+1}")
                break
        await ctx.send(embed=embed)
    
    @commands.command(name="leaderboard", aliases=["lb", "ranks"])
    async def leaderboard(self, ctx, page=1):
        leaderboard = []
        async for user in userdb.find({}):
            leaderboard.append((user["_id"], user["xp"]))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        total_pages = math.ceil(len(leaderboard) / 10)
        if page > total_pages or page < 1:
            await ctx.send("Invalid page number!")
            return
        start_index = (page - 1) * 10
        end_index = start_index + 10
        embed = discord.Embed(title=f"Global Leaderboard - Page {page}/{total_pages}", color=discord.Color.green())
        for i, user in enumerate(leaderboard[start_index:end_index], start=start_index+1):
            embed.add_field(name=f"{i}. {ctx.guild.get_member(user[0]).display_name}", value=f"XP: {user[1]}", inline=False)
        if page == 1:
            prev_page = None
        else:
            prev_page = page - 1
        if page == total_pages:
            next_page = None
        else:
            next_page = page + 1
        embed.set_footer(text=f"Previous Page: {prev_page} | Next Page: {next_page}")
        message = await ctx.send(embed=embed)
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await message.reply("Timed out! This message is now useless.", delete_after=2)
            await message.delete()
            return
        else:
            if str(reaction.emoji) == "⬅️" and prev_page:
                await message.delete()
                await self.leaderboard(ctx, prev_page)
            elif str(reaction.emoji) == "➡️" and next_page:
                await message.delete()
                await self.leaderboard(ctx, next_page)
            else:
                await message.reply("Invalid reaction!", delete_after=2)

    @commands.command(name="addxp", usage="`<member> <amount>`")
    @commands.is_owner()
    async def addxp(self, ctx, member: discord.Member, amount: int):
        if (await userdb.find_one({"_id": member.id})) is None:
            await self.add_user(member)
            return await ctx.send("User not found! Please try again!")
        else:
            await self.user_xp(ctx, member, amount)
            return await ctx.send(f"Added {amount} XP to {member.display_name}!")
    
    @commands.command(name="removexp", usage="`<member> <amount>`")
    @commands.is_owner()
    async def removexp(self, ctx, member: discord.Member, amount: int):
        if (await userdb.find_one({"_id": member.id})) is None:
            await self.add_user(member)
            return await ctx.send("User not found! Please try again!")
        else:
            await self.user_xp(ctx, member, -amount)
    
    @commands.command(name="setxp", usage="`<member> <amount>`")
    @commands.is_owner()
    async def setxp(self, ctx, member: discord.Member, amount: int):
        if (await userdb.find_one({"_id": member.id})) is None:
            await self.add_user(member)
            return await ctx.send("User not found! Please try again!")
        else:
            await self.user_xp(ctx, member, amount, True)
            
    async def user_xp(self, ctx, member, amount, set = False):
        user = await userdb.find_one({"_id": member.id})
        if set:
            await userdb.update_one(
                {"_id": member.id},
                {"$set": {"xp": amount}}
            )
            await userdb.update_one(
                {"_id": member.id},
                {"$set": {"level": 0}}
            )
            return await ctx.send(f"Set {member.display_name}'s XP to {amount}!")
        else:
            await userdb.update_one(
                {"_id": member.id},
                {"$inc": {"xp": amount}}
            )
            await userdb.update_one(
                {"_id": member.id},
                {"$set": {"level": 0}}
            )
            await ctx.send(f"Added {amount} XP to {member.display_name}!")
       
    @commands.command(name="reset")
    @commands.is_owner()
    async def reset(self, ctx):
        await self.reset_all(ctx)
    
    @commands.command(name="addall")
    @commands.is_owner()
    async def addall(self, ctx):
        await self.add_all(ctx)
    
def setup(bot):
    bot.add_cog(leveling(bot))


