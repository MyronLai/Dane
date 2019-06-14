import discord
from discord.ext import commands
from utils import *
class AdminTextCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.database = self.client.database

    @commands.command()
    async def setmuterole():
        pass

    '''
    Command: Prune
    mass delete messages using TextChannel.purge() function, must ensure that the command is issued by an Administrator, and that the user id provided is not of an Admin on the server.
    '''
    @commands.command()
    async def prune(self, ctx, *args):
        if len(args) == 1:
            if ctx.channel.permissions_for(ctx.author).administrator:
                await prune_messages(ctx.message, int(user_id))
            else:
                print("Non-admin trying to use an admin command.")
        elif len(args) == 0:
            print("Prune all messages")
def setup(bot):
    bot.add_cog(AdminTextCommands(bot))