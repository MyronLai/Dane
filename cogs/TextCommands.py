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
        embed=discord.Embed()
        cursor = self.database.cursor()
        cursor.execute("SELECT help_msg FROM GuildConfigurables WHERE guild_id=" + str(ctx.guild.id))
        result = cursor.fetchall()
        if len(result) == 0:
            print("Guild does not exist. Add them with defaults.")
            cursor.execute("INSERT INTO GuildConfigurables (guild_id) VALUES ({})".format(str(ctx.guild.id)))
        else:
            if result[0][0] is None:
                embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
                embed.description='No help message set!'
                embed.set_footer(text='Please set a help message: ?sethelp')
                await ctx.channel.send(embed=embed)
            else:
                embed.title='Information For {}'.format(ctx.guild.name)
                embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
                embed.description=result[0][0]
                embed.set_footer(text=ctx.guild.name)
                await ctx.channel.send(embed=embed)
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
        print("hello?")
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