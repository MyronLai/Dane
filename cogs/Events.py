import discord
from discord.ext import commands
import time
import datetime 
import random
import threading
import asyncio
import json

bucket = commands.CooldownMapping.from_cooldown(5, 3, commands.BucketType.member)

class DaneBotEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.database = self.client.database
        
    @commands.Cog.listener()
    async def on_ready(self):

        guilds = self.client.guilds
        cursor = self.database.cursor()
        for g in guilds:
            cursor.execute("INSERT INTO GUILDS VALUES ('{}','{}', '{}', '{}', '{}')".format(g.id, g.owner.id, g.name, len(g.members), g.created_at))

        print('Logged in as ' + self.client.user.name + '#' + self.client.user.discriminator)
        print(self.database)
        await self.client.change_presence(activity=discord.Game('Coding for ' + str(len(self.client.guilds))  + ' guilds.'))
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(type(error))
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed()
            embed.title="Command Error"
            embed.description=str(error)
            await ctx.channel.send(embed=embed)
        else:
            print(error)

    
    ''' 
        Get the Moderator Logs  channel from the  database and send the message there.
        
    '''
    @commands.Cog.listener()
    async def on_message_delete(self, message): # Print out a summary of the message deleted
        if message.author.bot:
            return
        msgString = message.content
        msgAuthor = message.author
        time = utc_to_local(message.created_at)
        id = message.id

        embed = discord.Embed(color=16007746)

        embed.title = "Message Deleted <" + str(id) +">"
        embed.add_field(name="Author", value=msgAuthor, inline=False)
        embed.add_field(name="Time", value=time, inline=False)
        embed.add_field(name="Message ID", value=id, inline=False)
        embed.add_field(name="Message", value=msgString)
        embed.set_author(name=msgAuthor, icon_url=msgAuthor.avatar_url)

        channels = message.guild.channels
        mod_channel = discord.utils.get(channels, name='mod-logs')
        await mod_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Add user to database
        try:
            cursor = self.database.cursor()
            cursor.execute("INSERT INTO Users VALUES(" + str(member.id) + "," + str(member.guild.id) + ", DEFAULT)")
            self.database.commit()
        except Exception as err:
            print(err)

        try:
            embed = discord.Embed(color=4303348)
            embed.set_author(name=self.client.user.name, icon_url=member.avatar_url)
            embed.set_footer(text="User joined")
        except Exception as err:
            print(err)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            pass
        else:
            member_log_channel = discord.utils.get(member.guild.channels, name='member-log')
            authorName = member.name + "#" + member.discriminator + " <" + str(member.id) + ">"
            embed = discord.Embed(color=16007489)
            embed.set_author(name=authorName, icon_url=member.avatar_url)
            embed.set_footer(text="User left")
            await member_log_channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):

        cursor = self.database.cursor()
        cursor.execute("SELECT mod_channel FROM GuildConfigurables WHERE guild_id={}".format(str(guild.id)))
        result = cursor.fetchall()
        if len(result) != 0:
            channel = discord.utils.get(member.guild.channels, id=int(result[0][0]))
            authorName = member.name + "#" + member.discriminator + " <" + str(member.id) + ">"
            embed = discord.Embed(color=16029762)
            embed.set_author(name=authorName, icon_url=member.avatar_url)
            embed.set_footer(text="User Banned")
            await channel.send(embed=embed)
        else:
            print("Needs to set a mod channel")
        

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        member_log_channel = discord.utils.get(guild.channels, name='mod-logs')
        authorName = user.name + "#" + user.discriminator + " <" + str(user.id) + ">"
        embed = discord.Embed(color=8314597)
        embed.set_author(name=authorName, icon_url=user.avatar_url)
        embed.set_footer(text="User Unbanned")
        await member_log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if bucket.update_rate_limit(message):
            muted_role = discord.utils.find(lambda role: role.name == 'Muted by Dane', message.guild.roles)
            if muted_role is not None:
                print("Role exists.")
                all_channels = message.guild.channels
                await message.author.add_roles(muted_role, reason="User was spamming.")
            else:
                muted_role = await message.guild.create_role(name='Muted by Dane') # Create the role...
                all_channels = message.guild.channels
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages=False
                overwrite.read_messages=True
                
                for channel in all_channels:
                    if channel.permissions_for(message.guild.me).manage_roles: # If the bot can manage permissions for channel, then overrwrite.
                        await channel.set_permissions(muted_role, overwrite=overwrite)

                # Mute the user by giving them the Muted role.
                await message.author.add_roles(muted_role, reason="User was spamming.")

            embed = discord.Embed()
            embed.title='Administrator Message'
            embed.description=message.author.name + ' was muted for 60 seconds.'
            await message.channel.send(embed=embed)
            await asyncio.sleep(60) # Sleep for 60 seconds, and then unmute the user.
            await message.author.remove_roles(muted_role, reason="Unmuting...")
            return
        
        elif message.content.startswith(self.client.command_prefix): # If user is issuing a command, don't give them XP.
            return
        else:
            pass

'''
function used to convert utc to local time
'''
def utc_to_local(dt):
    if time.localtime().tm_isdst:
        return dt - datetime.timedelta(seconds = time.altzone)
    else:
        return dt - datetime.timedelta(seconds = time.timezone)

def generate_xp():
    return random.randint(1, 50)

def setup(bot):
    bot.add_cog(DaneBotEvents(bot))