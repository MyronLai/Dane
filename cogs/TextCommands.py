import discord
from utils import *
from discord.ext import commands
import courses
import random
from database.dbutils import *
class TextCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.database = self.client.database
        
    @commands.command()
    async def help(self, ctx):
        await display_help(ctx, self.database)

    @commands.command()
    async def assign(self, ctx):
        await assignRole(self.client, ctx.message)

    ''' Remove a role from a user '''
    @commands.command()
    async def remove(self, ctx):
        await removeRole(self.client, ctx.message)

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