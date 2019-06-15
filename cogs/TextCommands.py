import discord
from utils import *
from discord.ext import commands
import courses
import random
from database.database import *

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

    @commands.command()
    async def subscribe(self, ctx):
        role = discord.utils.find(lambda role: role.name=='Subscribe', ctx.guild.roles)
        #voice = discord.utils.find(lambda channel: channel.id==int(voice_channel_id), ctx.guild.channels)

        #if voice is not None:
        embed=discord.Embed()
        if role is not None:
            await ctx.author.add_roles(role)
            embed.description='Subscribed!'
            await ctx.channel.send(embed=embed)
        else:
            embed.description='Role does not exist'
            await ctx.channel.send(embed=embed)
        '''else:
            embed.title='Error'
            embed.description='The role with id ' + int(voice_channel_id) + ' does not exist!'
            await ctx.channel.send(embed=embed)'''




def setup(bot):
    bot.add_cog(TextCommands(bot))