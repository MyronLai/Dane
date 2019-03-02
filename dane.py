import json
import discord
import asyncio

from commands import *
import courses

client = discord.Client()

with open('config/config.json') as f: # LOAD JSON FILE
    data = json.load(f) # LOAD JSON INTO data

CLIENT_TOKEN = data['token'] # STORE CLIENT TOKEN from JSON.

# -----------------

def isValidCommand(msg, command):
    return msg.startswith("?" + command)

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)
    await courses.getCourses()

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if isValidCommand(message.content, "help"): # True if command is '?help'
        await displayHelpDirectory(client, message.channel)

    elif isValidCommand(message.content, "bot"): # True if command is '?bot'
        print("Bot")

    elif isValidCommand(message.content, "assign"):
        await assignRole(client, message) # Adds a user to a role

    elif isValidCommand(message.content, "remove"):
        await removeRole(client, message)

    elif isValidCommand(message.content, "course"):
        await queryCourse(client, message)

@client.event
async def on_message_delete(message): # Print out a summary of the message deleted

    msgString = message.content
    msgAuthor = message.author
    time = message.timestamp
    id = message.id

    embed = discord.Embed()

    embed.title = "Message Deleted <" + id +">"

    embed.add_field(name="Author", value=msgAuthor, inline=False)
    embed.add_field(name="Time", value=time, inline=False)
    embed.add_field(name="Message ID", value=id, inline=False)
    embed.add_field(name="Message", value=msgString)
    embed.set_author(name=msgAuthor, icon_url=msgAuthor.avatar_url)

    embed.color = 16007746

    channels = message.server.channels
    mod_channel = discord.utils.get(channels, name='mod-logs')
    await client.send_message(mod_channel, embed=embed)

client.run(CLIENT_TOKEN) # Run the bot
