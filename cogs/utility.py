import discord, json, asyncio, datetime, time, motor
from discord.ext import commands

sniped_messages = {}
edited_messages = {}
afk_data = {}

with open("config.json") as f:
    config = json.load(f)

"""from ro_py import Client # type: ignore
client = Client()"""

class Utility(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        Pong! Sends the latency of the bot.
        """
        embed = discord.Embed(description=f":ping_pong: | Pong! `{round(self.bot.latency * 1000)}ms`", color=discord.Color.dark_purple())
        await ctx.send(embed=embed)

    @commands.command(name="lastfm", usage="<last.fm username>", aliases=["fm", 'lfm'])
    async def lastfm(self, ctx, user: str):
        """
        Displays a users current listening track from Last.fm
        """
        import requests
        import xml.etree.ElementTree as ET

        # Get API key from a file in the same directory as this file
        with open("config.json", "r") as f:
            config = json.load(f)
            api_key = config["lastfm_api_key"]

        url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=1&user={user}&api_key={api_key}&format=json"
        response = requests.get(url)
        data = response.json()
        tracks = data.get("recenttracks", {}).get("track", [])
        if tracks:
            track = tracks[0]
            artist = track["artist"]["#text"]
            title = track["name"]
            album = track["album"]["#text"]
            cover_art = track["image"][-1]["#text"]
            url = track["url"]
            print(cover_art)
            print(track)
            embed = discord.Embed(
                description=f"**{title}** by **{artist}**", 
                thumbnail=cover_art,
                color=discord.Color.blurple()
            )
            if album:
                embed.set_footer(text=f"Album: {album}")
            elif url:
                embed.set_author(url=url, name=f"{user} on Last.fm")
            await ctx.send(embed=embed)
    
    @commands.command(name="userinfo", usage="<member (optional)>", aliases=["ui"])
    async def userinfo(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        embed = discord.Embed(title=f"User Info - {member.name}#{member.discriminator}", description=member.mention, color=member.color)
        embed.set_thumbnail(url=member.avatar.url)
        badge_field = ""
        if member.id == config["lead"]:
            badge_field += '<:lead_developer:1252043061878325378>'
        if member.id in config["developers"]:
            badge_field += '<:peak_developer:1252043067741966440>'
        
        badges = {
            "staff": "<:Discord_Staff:1252043084091625563>",
            "discord_certified_moderator": "<:community_moderator:1252043167872585831>",
            "bug_hunter": "<:bug_hunter_standard:1252043073563922545>",
            "bug_hunter_level_2": "<:bug_hunter_level_2:1252043072410357780>",
            "active_developer": "<:active_developer:1252043070426452018>",
            "hypesquad": "<:hypesquad:1252047732231766198>",
            "hypesquad_brilliance": "<:hypesquad_brilliance_badge:1252043090600923267>",
            "hypesquad_balance": "<:hypesquad_balance_badge:1252043087350333450>",
            "hypesquad_bravery": "<:hypesquad_bravery_badge:1252043169021825144>",
            "early_supporter": "<:early_supporter:1252043085643517952>",
            "verified_bot": "<:verified_app:1252048210504187935>",
            "verified_bot_developer": "<:verified_bot_developer:1252043069231206420>",
            "partner": "<:partnered_server:1252043066588528711> "
        }

        for badge in member.public_flags.all():
            if badge.name in badges:
                badge_field += badges[badge.name]
                
        if member.premium_since:
            badge_field += '<a:boost:1252043070980100238>'
        if member.premium_since:
            badge_field += '<:nitro:1252043065724502138>'
            
        embed.add_field(name="Badges", value=badge_field, inline=False)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.display_name, inline=True)
        embed.add_field(name="Status", value=str(member.status), inline=True)
        embed.add_field(name="Bot?", value=str(member.bot), inline=True)
        embed.add_field(name="In Voice?", value=str(member.voice), inline=True)
        embed.add_field(name="Created At", value=f"<t:{round(member.created_at.timestamp())}:f>", inline=False)
        embed.add_field(name="Joined Server", value=f"<t:{round(member.joined_at.timestamp())}:R>", inline=True)
        if member.premium_since:
            embed.add_field(name="Boosting Since", value=f"<t:{round(member.premium_since.timestamp())}:f>", inline=False)
        join_pos = sorted(ctx.guild.members, key=lambda m: m.joined_at).index(member) + 1
        embed.add_field(name="Join Position", value=join_pos, inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name="roleusers", aliases=["ru", 'inrole', 'ir'])
    async def roleusers(self, ctx, *, role: discord.Role):
        """
        Lists all the users within a role, and if its their highest role or not
        """
        users = [member for member in role.members]
        messages = []
        for user in users:
            highest_role = user.roles[-1]
            if highest_role == role:
                is_highest = "Yes"
                user_name = f"{user.name}"
            if user.id == ctx.author.id:
                user_name = f"**{user.name}**"
            if user.id == self.bot.user.id:
                user_name = f"***{user.name}***"
            if user.id == ctx.guild.owner_id:
                user_name = f"**{user.name}** - :crown:"
            else:
                is_highest = "No"
                user_name = user.name
            messages.append(f"{user.mention} ({user_name})")
        embed = discord.Embed(title=f"Users in Role {role.name}", description="\n".join(messages), color=discord.Color.blurple())
        await ctx.send(embed=embed)
    
    @commands.command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        embed = discord.Embed(title=f"Avatar - {member.name}#{member.discriminator}", description=member.mention, color=member.color)
        embed.set_image(url=member.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="savatar", aliases=["sav", "spfp"])
    async def avatar(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        embed = discord.Embed(title=f"Server Avatar - {member.name}#{member.discriminator}", description=member.mention, color=member.color)
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="banner", aliases=['ub'])
    async def banner(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        embed = discord.Embed(title=f"User Banner - {member.name}#{member.discriminator}", description=member.mention, color=member.color)
        embed.set_thumbnail(url=member.banner.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.channel.id not in sniped_messages:
            sniped_messages[message.channel.id] = []
        sniped_messages[message.channel.id].insert(0, message)
        if len(sniped_messages[message.channel.id]) > 5:
            sniped_messages[message.channel.id].pop()
    
    @commands.command(name="snipe", aliases=["s"], usage="`<index>` `<channel>`")
    async def snipe(self, ctx, index: int = 1, channel: discord.TextChannel = None):
        """
        Snipe the most recent deleted message
        """
        if ctx.channel.id in sniped_messages:
            if len(sniped_messages[ctx.channel.id]) >= index:
                message = sniped_messages[ctx.channel.id][index-1]
                if message.attachments:
                    embed = discord.Embed(timestamp=message.created_at)
                    embed.set_footer(text=f"Message {index}/{len(sniped_messages[ctx.channel.id])} in #{ctx.channel.name}")
                    embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar.url)
                    embed.set_image(url=message.attachments[0])
                    return await ctx.send(message.content, embed=embed)
                elif 'tenor' in message.content:
                    embed = message.embeds[0]
                    embed.set_footer(text=f"Message {index}/{len(sniped_messages[ctx.channel.id])} in #{ctx.channel.name}")
                    embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar.url)
                    return await ctx.send(embed=embed)
                elif message.embeds:
                    embed = message.embeds[0]
                    embed.set_footer(text=f"Message {index}/{len(sniped_messages[ctx.channel.id])} in #{ctx.channel.name}")
                    embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar.url)
                    return await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=message.content, timestamp=message.created_at)
                    embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar.url)
                    embed.set_footer(text=f"Message {index}/{len(sniped_messages[ctx.channel.id])} in #{ctx.channel.name}")
                    return await ctx.send(embed=embed)
            else:
                await ctx.send(f"No deleted message at index {index}")
        else:
            await ctx.send("No deleted messages to snipe")
    
    @commands.command(name="clearsnipe", aliases=["cls", 'cs'])
    async def clearsnipe(self, ctx, channel: discord.TextChannel = None):
        """
        Clears the sniped messages for the channel
        """
        if channel is None:
            channel = ctx.channel
        if channel in sniped_messages:
            del sniped_messages[ctx.channel.id]
            await ctx.reply("Cleared.", delete_after=2)
            await ctx.message.delete()
            del sniped_messages[ctx.channel.id]
        else:
            await ctx.send("No deleted messages to clear")
            
    @commands.command(name="editsnipe", aliases=["es"])
    async def edit_snipe(self, ctx, index: int = 1):
        """
        Snipe the most recent edited message
        """
        if ctx.channel.id in edited_messages:
            if len(edited_messages[ctx.channel.id]) >= index:
                message = edited_messages[ctx.channel.id][index-1]
                before_content = message['before'].content
                after_content = message['after'].content
                embed = discord.Embed(color=discord.Color.blurple())
                embed.add_field(name="Before", value=before_content, inline=True)
                embed.add_field(name="After", value=after_content, inline=True)
                embed.set_author(name=f"{message['before'].author} ({message['before'].author.id})", icon_url=message['before'].author.avatar.url)
                embed.set_footer(text=f"Message {index}/{len(edited_messages[ctx.channel.id])} in {ctx.channel.name}")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No edited message at index {index}")
        else:
            await ctx.send("No edited messages to snipe")

    @commands.command(name="cleareditsnipe", aliases=["ces", "ce", 'ced'])
    @commands.has_permissions(manage_messages=True)
    async def clear_snipe(self, ctx):
        """
        Clears the sniped messages for the channel.

        This command deletes all the edited messages for the current channel.
        It requires the user to have the 'manage_messages' permission.

        Parameters:
            ctx (Context): The context of the command.
        """
        # Check if the current channel has any edited messages
        if ctx.channel.id in edited_messages:
            # Delete all the edited messages for the current channel
            del edited_messages[ctx.channel.id]
            await ctx.reply("Cleared.", delete_after=2)
            await ctx.message.delete()
            del edited_messages[ctx.channel.id]
        else:
            await ctx.send("No deleted messages to clear")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        elif before.content == after.content:
            return
        if before.channel.id not in edited_messages:
            edited_messages[before.channel.id] = []
        edited_messages[before.channel.id].insert(0, {"before": before, "after": after})
        if len(edited_messages[before.channel.id]) > 5:
            edited_messages[before.channel.id].pop()

    @commands.command(name="afk", usage="`<reason>`")
    async def afk(self, ctx, *, reason=None):
        """
        Set your status to AFK
        """
        afk_data[ctx.author.id] = {}
        afk_data[ctx.author.id]['reason'] = reason if reason else "AFK"
        afk_data[ctx.author.id]['time'] = time.time()
        await ctx.send(f"Set AFK. Reason: {discord.utils.escape_mentions(reason) if reason else 'AFK'}") # make mentions not mention :3

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # Check if the message mentions someone who is afk
        if message.mentions:
            for user in message.mentions:
                if user.id in afk_data:
                    afk_reason = afk_data[user.id]['reason']
                    afk_time = round(time.time() - afk_data[user.id]['time'])
                    hours, remainder = divmod(afk_time, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    embed = discord.Embed(title=f"{user.display_name} is AFK", description=f"Reason: {afk_reason}", color=discord.Color.purple())
                    embed.add_field(name="AFK for", value=f"{str(hours) + 'h ' if int(hours) > 0 else ''}{str(minutes) + 'm ' if int(minutes) > 0 else ''}{str(seconds) + 's' if int(seconds) > 0 else ''}")
                    await message.reply(embed=embed, delete_after=3)
        if message.author.id in afk_data:
            time_afk = time.time() - afk_data[message.author.id]['time']
            if time_afk > 1:
                afk_time = round(time.time() - afk_data[message.author.id]['time'])
                hours, remainder = divmod(afk_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                embed = discord.Embed(description=f"Welcome back, you were afk for `{str(hours) + 'h ' if int(hours) > 0 else ''}{str(minutes) + 'm ' if int(minutes) > 0 else ''}{str(seconds) + 's' if int(seconds) > 0 else ''}`", color=discord.Color.green())
                await message.reply(embed=embed, delete_after=3)
                del afk_data[message.author.id]

    @commands.command(name="unafk", usage="Make someone no longer afk")
    @commands.has_permissions(manage_messages=True)
    async def unafk(ctx, user: discord.Member):
        if user.id in afk_data:
            time_afk = time.time() - afk_data[user.id]['time']
            if time_afk > 1:
                afk_time = round(time.time() - afk_data[user.id]['time'])
                hours, remainder = divmod(afk_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                embed = discord.Embed(
                    description=f"Welcome back {user.mention}, you were afk for `{str(hours) + 'h ' if int(hours) > 0 else ''}{str(minutes) + 'm ' if int(minutes) > 0 else ''}{str(seconds) + 's' if int(seconds) > 0 else ''}`",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed, delete_after=3)
                del afk_data[user.id]
            else:
                await ctx.send(f"{user.display_name} is no longer afk.")
        else:
            await ctx.send(f"{user.display_name} is not currently afk.")
                        
            # ks will this work idk python

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"An error occurred while executing the command: ```\n{error.original}```")

def setup(bot):
    bot.add_cog(Utility(bot))

