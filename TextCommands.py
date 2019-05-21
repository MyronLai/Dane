import discord
from commands import *
from discord.ext import commands

class TextCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def help(self, ctx):
        await displayHelpDirectory(ctx.channel)

    @commands.command()
    async def assign(self, ctx):
        await assignRole(self.client, ctx.message)

    @commands.command()
    async def remove(self, ctx):
        await removeRole(self.client, ctx.message)

    @commands.command()
    async def course(self, ctx):
        await queryCourse(ctx, ctx.message)

    @commands.command()
    async def ban(self, ctx, user_id, reason):
        await assignUserBan(ctx, user_id, reason)
    

    '''
    mass delete messages using TextChannel.purge() function, must ensure that the command is issued by an Administrator, and that the user id provided is not of an Admin on the server.
    '''
    @commands.command()
    async def prune(self, ctx, user_id):
        await pruneMessages(ctx.message, int(user_id))

def setup(bot):
    bot.add_cog(TextCommands(bot))