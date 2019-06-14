import discord
from discord.ext import commands

class AdminTextCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.database = self.client.database
def setup(bot):
    bot.add_cog(AdminTextCommands(bot))