import json
import discord
import asyncio

from commands import displayHelpDirectory, assignRole

client = discord.Client()

with open('config.json') as f: # LOAD JSON FILE
    data = json.load(f) # LOAD JSON INTO data

CLIENT_TOKEN = data['token'] # STORE CLIENT TOKEN from JSON.

def isValidCommand(msg, command):
    return msg.startswith("?" + command)

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)

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
        print("Remove a role")

client.run(CLIENT_TOKEN) # Run the bot
