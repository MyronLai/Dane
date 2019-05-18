import json
import discord
import datetime
import time
from discord.ext import commands 
from commands import *

import reaction
import courses

client = commands.Bot(command_prefix='?', help_command=None)
reactionBot = reaction.ReactionBot(client)
with open('config/config.json') as f: # LOAD JSON FILE
    data = json.load(f) # LOAD JSON INTO data

CLIENT_TOKEN = data['token'] # STORE CLIENT TOKEN from JSON.

# -----------------

extensions = ['reaction']

if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)
        
@client.command()
async def help(ctx):
    await displayHelpDirectory(ctx.channel)

@client.command()
async def assign(ctx):
    await assignRole(client, ctx.message)

@client.command()
async def remove(ctx):
    await removeRole(client, ctx.message)

@client.command()
async def course(ctx):
    await queryCourse(ctx, ctx.message)

'''
mass delete messages using TextChannel.purge() function, must ensure that the command is issued by an Administrator, and that the user id provided is not of an Admin on the server.
'''
@client.command()
async def prune(ctx, user_id):
    await pruneMessages(ctx.message, int(user_id))

@client.event
async def on_command_error(ctx, error):
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

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)

@client.event
async def on_message_delete(message): # Print out a summary of the message deleted

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

@client.event
async def on_member_join(member):
    member_log_channel = discord.utils.get(member.server.channels, name='member-log')
    authorName = member.name + "#" + member.discriminator + " <" + member.id + ">"
    embed = discord.Embed(color=4303348)
    embed.set_author(name=authorName, icon_url=member.avatar_url)
    embed.set_footer(text="User joined")
    # Add user to Great Dane Role. 
    await member_log_channel.send(embed=embed)

@client.event
async def on_member_remove(member):
    member_log_channel = discord.utils.get(member.server.channels, name='member-log')
    authorName = member.name + "#" + member.discriminator + " <" + member.id + ">"
    embed = discord.Embed(color=16007489)
    embed.set_author(name=authorName, icon_url=member.avatar_url)
    embed.set_footer(text="User left")
    await member_log_channel.send(embed=embed)

@client.event
async def on_member_ban(member):
    member_log_channel = discord.utils.get(member.server.channels, name='mod-logs')
    authorName = member.name + "#" + member.discriminator + " <" + member.id + ">"
    embed = discord.Embed(color=16029762)
    embed.set_author(name=authorName, icon_url=member.avatar_url)
    embed.set_footer(text="User Banned")
    await member_log_channel.send(embed=embed)

@client.event
async def on_member_unban(server, user):
    member_log_channel = discord.utils.get(server.channels, name='mod-logs')
    authorName = user.name + "#" + user.discriminator + " <" + user.id + ">"
    embed = discord.Embed(color=8314597)
    embed.set_author(name=authorName, icon_url=user.avatar_url)
    embed.set_footer(text="User Unbanned")
    await member_log_channel.send(embed=embed)

def utc_to_local(dt):
    if time.localtime().tm_isdst:
        return dt - datetime.timedelta(seconds = time.altzone)
    else:
        return dt - datetime.timedelta(seconds = time.timezone)

client.run(CLIENT_TOKEN) # Run the bot
