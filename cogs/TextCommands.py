import discord
from discord.ext import commands
import random
from database.dbutils import *
from utilities.utils import *
from utilities.courses import *

class TextCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.database = self.client.database
        
    @commands.command()
    async def help(self, ctx):
        await display_help(ctx, self.database)
    
    '''
        Get a List of "Assignable" roles, i.e: Non-Admin, Non-Mod, Non-Permission roles.
        Iterate through the Guild Roles, check if it has Permissions.
        We need to make sure the Role does not have these permissions:
            - Administrator
            - Manage Server
            - Manage Roles
            - Manage Channels
            - Kick Members
            - Ban Members
            - Manage Nicknames
            - Manage Emojis
            - Manage Webhooks
    '''
    @commands.command()
    async def me(self, ctx, *, arg):
        await add_roles(ctx, arg)
    
    ''' Remove a role from a user '''
    @commands.command()
    async def notme(self, ctx, *, arg):
        await remove_roles(ctx, arg)

    @commands.command()
    async def course(self, ctx):
        await queryCourse(ctx, ctx.message)

    @commands.command()
    async def dice(self, ctx):
        message = ctx.message
        await message.channel.send('Would you like to roll the die? Y/N')
        def check(m):
            return (m.content.lower() == 'y' or m.content.lower() == 'yes') and m.author.id == message.author.id
        
        msg = await self.client.wait_for('message', check=check)
        await message.channel.send('You rolled a ' +str(random.randint(1, 6)))
    
def setup(bot):
    bot.add_cog(TextCommands(bot))