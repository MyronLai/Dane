import discord
from discord.ext import commands
import time
import datetime 

class DaneBotEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as ' + self.client.user.name)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

        if ctx.message.channel.permissions_for(ctx.message.author).administrator:
            if ctx.command.name == 'prune':
                # Send an embed
                embed = discord.Embed()
                embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                embed.description = 'Error: ' + str(error)
                embed.color = 16042050

                await ctx.channel.send(embed=embed)
        else:
            print('Non admin trying to use admin command')

    
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
        member_log_channel = discord.utils.get(member.guild.channels, name='member-log')
        authorName = member.name + "#" + member.discriminator + " <" + str(member.id) + ">"
        roles = discord.utils.get(member.guild.roles, name='Great Dane')
        
        if roles is not None:
            await member.add_roles(roles)

        embed = discord.Embed(color=4303348)
        embed.set_author(name=authorName, icon_url=member.avatar_url)
        embed.set_footer(text="User joined")
        # Add user to Great Dane Role. 
        await member_log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        member_log_channel = discord.utils.get(member.guild.channels, name='member-log')
        authorName = member.name + "#" + member.discriminator + " <" + str(member.id) + ">"
        embed = discord.Embed(color=16007489)
        embed.set_author(name=authorName, icon_url=member.avatar_url)
        embed.set_footer(text="User left")
        await member_log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        member_log_channel = discord.utils.get(member.guild.channels, name='mod-logs')
        authorName = member.name + "#" + member.discriminator + " <" + str(member.id) + ">"
        embed = discord.Embed(color=16029762)
        embed.set_author(name=authorName, icon_url=member.avatar_url)
        embed.set_footer(text="User Banned")
        await member_log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        member_log_channel = discord.utils.get(guild.channels, name='mod-logs')
        authorName = user.name + "#" + user.discriminator + " <" + str(user.id) + ">"
        embed = discord.Embed(color=8314597)
        embed.set_author(name=authorName, icon_url=user.avatar_url)
        embed.set_footer(text="User Unbanned")
        await member_log_channel.send(embed=embed)

'''
function used to convert utc to local time
'''
def utc_to_local(dt):
    if time.localtime().tm_isdst:
        return dt - datetime.timedelta(seconds = time.altzone)
    else:
        return dt - datetime.timedelta(seconds = time.timezone)


def setup(bot):
    bot.add_cog(DaneBotEvents(bot))