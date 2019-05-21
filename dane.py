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

extensions = ['reaction', 'TextCommands', 'Events']

if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)

def utc_to_local(dt):
    if time.localtime().tm_isdst:
        return dt - datetime.timedelta(seconds = time.altzone)
    else:
        return dt - datetime.timedelta(seconds = time.timezone)

client.run(CLIENT_TOKEN) # Run the bot
