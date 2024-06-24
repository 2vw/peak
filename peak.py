import discord, time, asyncio, os, json
from discord.ext import commands

with open("config.json") as f:
    config = json.load(f)

# make it do polls n shit
# announce funny shit
# moderate - on the way
# cosmetics
# manage verification
# role stuff - 25% done
# and other shit - ???

def getprefix(bot, message):
    if message.guild is None:
        return ["p!", "p?", "p.", "P!", "P?", "P."]
    if message.guild.id == 1238555988538167306:
        return ['p!', '?', ',']
    else:
        return ["p!"]

bot = commands.AutoShardedBot(command_prefix=getprefix, intents=discord.Intents.all(), strip_after_prefix=True)
cmtotal = 0
uptime = time.time()


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    await bot.change_presence(activity=discord.Streaming(name="ks's brains on the wall", url="https://twitch.tv/ksiscute"))


    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'cogs.{filename[:-3]}') # :-3
            except Exception as e:
                print(e)


@bot.before_invoke
async def before_invoke(ctx):
    global cmtotal
    cmtotal += 1

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command(name="stats")
async def stats(ctx):
    embed = discord.Embed(title="Bot Stats", color=discord.Color.dark_purple())
    embed.add_field(name="Guild", value=ctx.guild.name, inline=True)
    embed.add_field(name="Shard", value=f"{ctx.guild.shard_id + 1}/{bot.shard_count}", inline=True)
    embed.add_field(name="Commands This Session", value=f"`{cmtotal}`", inline=True)
    time_diff = round(time.time() - uptime)
    hours, remainder = divmod(time_diff, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    embed.add_field(name="Uptime", value=f"`{time_str}`", inline=True)
    embed.add_field(name="Latency", value=f"`{round(bot.latency * 1000)}ms`", inline=True)
    embed.set_footer(text=f"Peak v{config["version"]}")
    await ctx.send(embed=embed)

"""@bot.command(name="notepad", aliases=["np", 'tellks'], usage="`<text>`")
async def notepad(ctx, *, text):
    ""
    Open a notepad on ks' computer, and write text to it.

    Args:
        ctx: The context of the command.
        text: The text to be written in the notepad.txt file.
    ""
    with open("notepad.txt", "w") as f:
        f.write(text)
    await ctx.send("Opening notepad.txt on ks' computer...")
    os.startfile("notepad.txt")"""

"""@bot.command(name="edge", aliases=["tempadmin", "ta"])
async def tempadmin(ctx, role: discord.Role):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You must have administrator permissions to use this command")
        return
    permissions = discord.Permissions()
    permissions.administrator = True
    await role.edit(permissions=permissions, reason="Added administrator permissions")
    await ctx.send(f"Gave {role.name} administrator permissions for 3 seconds")
    await asyncio.sleep(3)
    await role.edit(permissions=discord.Permissions(), reason="Removed administrator permissions")
    await ctx.send(f"Removed administrator permissions from {role.name}")"""

# rock
bot.run(config['token'])