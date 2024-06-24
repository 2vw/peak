import discord, asyncio, datetime
from discord.ext import commands

class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command(name="strip", aliases=["demote", 'permstrip', 'ps'], usage="<member> <reason (optional)>")
    async def strip(self, ctx, member: discord.Member=None, *, reason:str=None):
        """
        Strips all roles with administrator, ban, kick, manage permissions from a member
        """
        if not member:
            embed = discord.Embed(title="Role Strip", color=discord.Color.red())
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.usage}`", inline=False)
            embed.add_field(name="Examples", value=f"`{ctx.prefix}{ctx.command.qualified_name} ks garbage staff member`", inline=False)
            await ctx.send(embed=embed)
            return

        if not ctx.me.guild_permissions.manage_roles:
            await ctx.send("I don't have permission to manage roles. Please give me the `manage_roles` permission")
            return
        elif not ctx.author.guild_permissions.administrator:
            await ctx.send("You must have administrator permissions to use this command")
            return
        elif member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot strip a member with a role higher than or equal to your own")
            return
        elif ctx.guild.me.top_role < member.top_role:
            await ctx.send("I cannot strip a member with a role higher than my own")
            return
        elif member == ctx.author:
            await ctx.send("You cannot strip yourself!")
            return
        elif member == ctx.guild.me:
            await ctx.send("You cannot strip me!") # pause
            # horny bastard, peak...
            return
        
        roles = [role for role in member.roles if role.permissions.administrator or role.permissions.ban_members or role.permissions.kick_members or role.permissions.manage_guild or role.permissions.moderate_members or role.permissions.manage_messages or role.permissions.manage_channels or role.permissions.manage_guild or role.permissions.manage_webhooks]
        if not roles:
            embed = discord.Embed(title="Role Strip", color=discord.Color.red())
            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Stripped Roles", value="No roles to strip from this member", inline=False)
            await ctx.send(embed=embed)
            return
        await member.edit(roles=[role for role in member.roles if role not in roles], reason=reason)
        embed = discord.Embed(title="Role Stripped", color=discord.Color.green())
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="Stripped Roles", value=", ".join(role.name for role in roles), inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name="role", usage="<member> <role>", aliases=["giverole", "r", 'addrole'])
    async def role(self, ctx, member: discord.Member = None, *, role_name: str = None):
        """
        Adds or removes a role from a member
        """
        if not member or not role_name:
            embed = discord.Embed(title="Role", color=discord.Color.red())
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.usage}`", inline=False)
            embed.add_field(name="Examples", value=f"`{ctx.prefix}{ctx.command.qualified_name} ks garbage staff member`\n`{ctx.prefix}{ctx.command.qualified_name} @Pineapple#1234 Pineapple`", inline=False)
            await ctx.send(embed=embed)
            return
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You must have `manage_roles` permission to use this command")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot add/remove a role from a member with a role higher than or equal to your own")
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send("I cannot add/remove a role from a member with a role higher than my own")
            return # faggy waggy
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"Role {role_name} does not exist")
            return
        if role >= ctx.guild.me.top_role:
            await ctx.send("I cannot add/remove a role higher than my own")
            return
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(title="Role Removed", color=discord.Color.red())
        else:
            await member.add_roles(role)
            embed = discord.Embed(title="Role Added", color=discord.Color.green())
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="Role", value=role.mention, inline=False)
        await ctx.send(embed=embed)
    @commands.command(name="purge", aliases=["clear"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """
        Deletes a number of messages
        """
        if amount is None:
            await ctx.send("Usage: `purge <number>`")
            return
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You must have `manage_messages` permission to use this command")
            return
        if amount > 1000:
            await ctx.send("You cannot delete more than 1000 messages at a time")
            return
        else:
            max_purge_amount = 100 if amount <= 100 else 250
            for i in range(0, amount, max_purge_amount):
                purge_amount = min(max_purge_amount, amount - i)
                await ctx.channel.purge(limit=purge_amount + 1)
            await ctx.send(f"Deleted {amount} messages!", delete_after=5)

    def convert_timestamp(self, timestamp):
        unit = timestamp[-1]
        value = timestamp[:-1]
        if unit == "d":
            return int(value) * 86400
        elif unit == "h":
            return int(value) * 3600
        elif unit == "m":
            return int(value) * 60
        elif unit == "s":
            return int(value)
        else:
            return None

    @commands.command(name="ban", aliases=["softban"], usage="<member> <reason> [duration] [delete_message_days=7]",)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member=None, *, reason: str=None, duration: str=None, delete_message_days: int=7):
        if not member:
            embed = discord.Embed(title="Ban", color=discord.Color.red())
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.usage}`", inline=False)
            embed.add_field(name="Examples", value=f"`{ctx.prefix}{ctx.command.qualified_name} ks garbage staff member`", inline=False)
            await ctx.send(embed=embed)
            return
        if not ctx.author.guild_permissions.ban_members:
            await ctx.send("You must have `ban_members` permission to use this command")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot ban a member with a role higher than or equal to your own")
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send("I cannot ban a member with a role higher than my own")
            return
        if not reason:
            reason = "No reason provided"
        await member.ban(reason=reason, delete_message_days=delete_message_days)
        if duration:
            duration = self.convert_timestamp(duration)
            await ctx.send(f"Banned *{member.name}* for {duration}\n{reason}")
            await asyncio.sleep(duration)
            await member.unban(reason="Duration of ban expired")
        else:
            await ctx.send(f"Banned *{member.name}* permanently for **{reason}**")
            
    @commands.command(name="unban", usage="<member> <reason>")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member, reason:str=None):
        if not ctx.author.guild_permissions.ban_members:
            await ctx.send("You must have `ban_members` permission to use this command")
            return
        banned_users = ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"Unbanned *{user.name}*")
                return

    @commands.command(name="kick", usage="<member> <reason>", aliases=["softkick", 'remove', 'delete', 'rape'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member=None, *, reason: str=None):
        if not member:
            embed = discord.Embed(title="Kick", color=discord.Color.red())
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.usage}`", inline=False)
            embed.add_field(name="Examples", value=f"`{ctx.prefix}{ctx.command.qualified_name} ksiscute garbage weirdo`", inline=False)
            await ctx.send(embed=embed)
            return
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send("You must have `kick_members` permission to use this command")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot kick a member with a role higher than or equal to your own")
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send("I cannot kick a member with a role higher than my own")
            return
        if not reason:
            reason = "No reason provided"
        await member.kick(reason=reason)
        await ctx.send(f"Kicked *{member.name}* for **{reason}**")

    @commands.command(name="nick", usage="<member> <nickname>")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member=None, *, nickname=None):
        if not member:
            embed = discord.Embed(title="Nickname", color=discord.Color.red())
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.usage}`", inline=False)
            embed.add_field(name="Examples", value=f"`{ctx.prefix}{ctx.command.qualified_name} ksiscute peak user`", inline=False)
            await ctx.send(embed=embed)
            return
        if not ctx.author.guild_permissions.manage_nicknames:
            await ctx.send("You must have `manage_nicknames` permission to use this command")
            return
        if not nickname:
            await ctx.send("You must provide a nickname")
            return
        await member.edit(nick=nickname)
        await ctx.send(f"Changed nickname of *{member.name}* to **{nickname}**")
        
    @commands.command(name="mute", usage="<member> <reason> [duration]", aliases=["tempmute", 'timeout', 'tm'])
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member=None, *, reason: str=None, duration: str=None):
        if not member:
            embed = discord.Embed(title="Mute", color=discord.Color.red())
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.usage}`", inline=False)
            embed.add_field(name="Examples", value=f"`{ctx.prefix}{ctx.command.qualified_name} ksiscute \"garbage staff member\" 10m`\n`{ctx.prefix}{ctx.command.qualified_name} ks ewwww 1h`", inline=False)
            await ctx.send(embed=embed)
            return
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You must have `manage_messages` permission to use this command")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot mute a member with a role higher than or equal to your own")
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send("I cannot mute a member with a role higher than my own")
            return
        if not reason:
            reason = "No reason provided"
        if not duration:
            duration = datetime.datetime.now() + datetime.timedelta(days=3*365)
        else:
            duration = datetime.datetime.fromtimestamp(duration)
        await ctx.send(f"Muted *{member.name}* for **{reason}**")
        await member.timeout(duration, reason=reason)

    @commands.command(name="admins")
    async def admins(self, ctx):
        """
        Shows all admins in the server (all users with the administrator permission)
        """
        admins = [member.name for member in ctx.guild.members if member.guild_permissions.administrator]
        bots = [member.name for member in ctx.guild.members if member.guild_permissions.administrator and member.bot]
        users = [member.name for member in ctx.guild.members if member.guild_permissions.administrator and not member.bot]

        embed = discord.Embed(title="Admins", color=discord.Color.dark_purple())
        embed.add_field(name="Bots With Admin", value=", ".join(bots), inline=True)
        embed.add_field(name="Users With Admin", value=", ".join(users), inline=True)
        embed.add_field(name="Total Admin Count", value=len(admins), inline=False)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")

        await ctx.send(embed=embed)

    @commands.command(name="unmute", usage="<member> <reason>")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str=None):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You must have `manage_messages` permission to use this command")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot unmute a member with a role higher than or equal to your own")
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send("I cannot unmute a member with a role higher than my own")
            return
        if not reason:
            reason = "No reason provided"
        await ctx.send(f"Unmuted *{member.name}* for **{reason}**")
        await member.timeout(None, reason=reason)
    
    @commands.command(name="nuke", usage="<channel>")
    @commands.has_permissions(manage_channels=True)
    async def duplicate(self, ctx, channel: discord.TextChannel=None):
        """
        Duplicates the channel, then deletes the old one, and sends a message in the new one
        """
        if not channel:
            channel = ctx.channel
        overwrites = channel.overwrites
        position = channel.position
        name = channel.name
        topic = channel.topic
        category = channel.category

        new_channel = await ctx.guild.create_text_channel(
            name=name, 
            position=position, 
            overwrites=overwrites, 
            topic=topic,
            category=category
        )
        await channel.delete()
        await new_channel.send(f"This channel has been nuked by {ctx.author.mention}!")
    

    @commands.command(name="temprole", usage="<member> <role> <duration>", aliases=["tempaddrole"])
    async def temprole(self, ctx, member: discord.Member, role_name: str, duration: str):
        """
        Temporarily gives a member a role, then removes it after a set duration
        """
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role_name in [role.name for role in member.roles]:
            error_embed = discord.Embed(description=f"{member.mention} already has the {role_name} role", color=discord.Color.red())
            await ctx.send(embed=error_embed)
            return
        if not ctx.author.guild_permissions.manage_roles:
            error_embed = discord.Embed(description="You must have `manage_roles` permission to use this command", color=discord.Color.red())
            await ctx.send(embed=error_embed)
            return
        if member.top_role >= ctx.author.top_role:
            error_embed = discord.Embed(description="You cannot add/remove a role from a member with a role higher than or equal to your own", color=discord.Color.red())
            await ctx.send(embed=error_embed)
            return
        if ctx.guild.me.top_role < member.top_role:
            error_embed = discord.Embed(description="I cannot add/remove a role from a member with a role higher than my own", color=discord.Color.red())
            await ctx.send(embed=error_embed)
            return
        if not role:
            error_embed = discord.Embed(description=f"Role {role_name} does not exist", color=discord.Color.red())
            await ctx.send(embed=error_embed)
            return
        if role >= ctx.guild.me.top_role:
            error_embed = discord.Embed(title="Error", description="I cannot add/remove a role higher than my own", color=discord.Color.red())
            await ctx.send(embed=error_embed)
            return
        else:
            await member.add_roles(role)
            await ctx.send(embed=discord.Embed(title="Role Added", description=f"Added {role.mention} to {member.mention} for {duration}", color=discord.Color.green()))
            await asyncio.sleep(self.convert_timestamp(duration))
            await member.remove_roles(role)
            await ctx.send(embed=discord.Embed(title="Role Removed", description=f"Removed {role.mention} from {member.mention} after {duration}", color=discord.Color.red()))



def setup(bot):
    bot.add_cog(Moderation(bot))


