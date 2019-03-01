import json
import discord
import asyncio

client = discord.Client()

with open('config.json') as f: # LOAD JSON FILE
    data = json.load(f) # LOAD JSON INTO data

CLIENT_TOKEN = data['token'] # STORE CLIENT TOKEN from JSON.

client.run(CLIENT_TOKEN) # Run the bot
