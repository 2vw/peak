import discord, asyncio, aiohttp, json, requests, random
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="fuck")
    @commands.is_nsfw()
    async def fuck(self, ctx, member: discord.Member=None):
        """
        Fucks an NSFW image
        """
        if member is None:
            return await ctx.reply("Bro.. are u that lonely? Damn...")
        images = [
            "https://rule34.xxx//images/830/e05a9815c6bfa0e5b00d59d1c325a724.gif?10409259",
            "https://us.rule34.xxx//images/830/e3ffc2689693e24b14f75f7735de6269.gif?10408690",
            "https://us.rule34.xxx//images/830/038266818c12ad0a93b4b1e9172c5d7f.gif?10408101",
            "https://us.rule34.xxx//images/830/6d3390cdc1f85970c5494f8d1e2dd43611d13fe5.gif?10407345",
            "https://us.rule34.xxx//images/2874/fed010ce66cfab915470072d94ca6c34.gif?10365659"
        ]
        embed = discord.Embed(color=discord.Color.red(), title=f"Woah... {ctx.author.display_name}.. wyd? | <:AkagiMiriaWink:1247698918012096564>", description=f"{ctx.author.display_name} is fucking {member.display_name}!")
        await ctx.send(embed=embed.set_image(url=random.choice(images)))
    @commands.command(name="ship") # kys pea
    async def ship(self, ctx, member1: discord.Member, member2: discord.Member=None):
        """
        Calculates a percentage of compatibility between two members
        """
        
        if not member2:
            member2 = ctx.author
        
        # Calculate the compatibility percentage
        compatibility = ((member1.joined_at.timestamp() + member2.joined_at.timestamp() + member1.created_at.timestamp() + member2.created_at.timestamp() + len(member1.name) + len(member2.name)) // 2) % 100
        # if u change this so u can goon im raping you
        # touch the algo i touch you

        # Create an embed with the compatibility percentage
        color = discord.Color.red() if compatibility <= 50 else discord.Color.orange() if 50 < compatibility <= 75 else discord.Color.green()
        heart = '<a:9Mpink_heart4:1248064257778782289>' * int(compatibility / 10) + '<a:heartbroken:1249470534392086609>' * (10 - int(compatibility / 10))
        embed = discord.Embed(title=f"{member1.name} and *{member2.name}*", description=f"Compatibility: {round(compatibility)}% \n {heart}", color=color)
        await ctx.send(embed=embed)

    @commands.command(name="kiss")
    async def kiss(self, ctx, member: discord.Member=None):
        """
        Kiss another member
        """
        
        if not member:
            member = ctx.author
        
        # Create an embed with the kiss
        embed = discord.Embed(title=f"{ctx.author.name} has kissed {member.name}!", color=discord.Color.red())
        embed.set_image(url="https://media1.tenor.com/m/_X0Fb3lhi3AAAAAC/anime.gif")
        await ctx.send(embed=embed)

    @commands.command(name="hug")
    async def hug(self, ctx, member: discord.Member=None):
        """
        Hug another member
        """
        
        if not member:
            member = ctx.author
        
        # Create an embed with the hug
        embed = discord.Embed(title=f"{ctx.author.name} has hugged {member.name}!", color=discord.Color.red())
        embed.set_image(url="https://media1.tenor.com/m/c2SMIhi33DMAAAAC/cuddle-bed-hug.gif")
        await ctx.send(embed=embed)

    @commands.command(name="pat")
    async def pat(self, ctx, member: discord.Member=None):
        """
        Pat another member
        """
        
        if not member:
            member = ctx.author
        
        # Create an embed with the pat
        embed = discord.Embed(title=f"{ctx.author.name} has patted {member.name}!", color=discord.Color.red())
        embed.set_image(url="https://media1.tenor.com/m/fro6pl7src0AAAAC/hugtrip.gif")
        await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild.id == 1238555988538167306:
            if "y/n" in message.content.lower():
                await message.add_reaction("✅")
                await message.add_reaction("❌")
            if "sob" in message.content.lower():
                await message.add_reaction("😭")
            if "skull" in message.content.lower():
                await message.add_reaction("💀")
            if "star" in message.content.lower():
                await message.add_reaction("⭐")
            if "hate" in message.content.lower():
                await message.add_reaction("🤬")
            if "nigger" in message.content.lower():
                await message.add_reaction("👹")
            if "nigga" in message.content.lower():
                await message.add_reaction("👿")
            if "gay" in message.content.lower():
                await message.add_reaction("🏳️‍🌈")
            if "fag" in message.content.lower():
                await message.add_reaction("🤢")
            if "nerd" in message.content.lower():
                await message.add_reaction("🤓")
            if "femboy" in message.content.lower():
                await message.add_reaction("<a:cum:1249891734457028671>")

def setup(bot):
    bot.add_cog(Misc(bot))
