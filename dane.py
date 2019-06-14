import json
import discord
from discord.ext import commands 
import reaction
from database.database import *
CONFIG_FILE = './config/config.json'

client = commands.Bot(command_prefix='?', help_command=None)
client.database = load_db(CONFIG_FILE)

with open(CONFIG_FILE) as f: # LOAD JSON FILE
    data = json.load(f) # LOAD JSON INTO data

CLIENT_TOKEN = data['token'] # STORE CLIENT TOKEN from JSON.

extensions = ['reaction', 'TextCommands', 'Events']

if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)

client.run(CLIENT_TOKEN) # Run the bot
