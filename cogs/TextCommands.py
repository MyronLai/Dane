import discord
from discord.ext import commands
import random
from database.dbutils import *
from utilities.utils import *
from utilities.courses import *
import json

class TextCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.database = self.client.database
    
    async def cmds(self, ctx):
        pass

    '''
        Notes:
            If the admin issues this command, check if their record exists in the GuildHelpMsg table. If it doesn't, insert them with default help_msg {}
    '''

    @commands.command()
    async def help(self, ctx):
        embed=discord.Embed()
        cursor = self.database.cursor()
        cursor.execute("SELECT help_msg FROM GuildHelpMsg WHERE guild_id=" + str(ctx.guild.id))
        result = cursor.fetchall()
        empty = {
            "msg" : "Set your help message!"
        }
        if len(result) == 0:
            print("Guild does not exist. Add them with defaults.")
            cursor.execute("INSERT INTO GuildHelpMsg (guild_id, help_msg) VALUES ({}, '{}')".format(str(ctx.guild.id), json.dumps(empty)))
            embed.description='You do not have a help message set. ?sethelp'
            await ctx.channel.send(embed=embed)
        else:
            if result[0][0] is None:
                icon_url="https://cdn.discordapp.com/icons/{}/{}.png".format(ctx.guild.id, ctx.guild.icon)
                embed.set_author(name=ctx.guild.name, icon_url=icon_url)
                embed.description='No help message set!'
                embed.set_footer(text='Please set a help message: ?sethelp')
                await ctx.channel.send(embed=embed)
            else:
                icon_url="https://cdn.discordapp.com/icons/{}/{}.png".format(ctx.guild.id, ctx.guild.icon)
                embed.set_author(name=ctx.guild.name, icon_url=icon_url)
                embed.description=json.loads(result[0][0])['msg']
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