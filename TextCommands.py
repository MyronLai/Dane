import discord
from commands import *
from discord.ext import commands
import courses
import random


class TextCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def help(self, ctx):
        await displayHelpDirectory(ctx.channel)

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

    '''
    Command: Ban
    admin command to ban users
    '''
    @commands.command()
    async def ban(self, ctx, user_id, reason):
        await assignUserBan(ctx, user_id, reason)
    
    '''
    Command: Prune
    mass delete messages using TextChannel.purge() function, must ensure that the command is issued by an Administrator, and that the user id provided is not of an Admin on the server.
    '''
    @commands.command()
    async def prune(self, ctx, user_id):
        await pruneMessages(ctx.message, int(user_id))
    
    @commands.command()
    async def kick(self, ctx, user_id, reason):
        await kickUser(ctx, int(user_id), reason)
        
    @commands.command()
    async def dice(self, ctx):
        message = ctx.message
        await message.channel.send('Would you like to roll the die? Y/N')
        def check(m):
            return (m.content.lower() == 'y' or m.content.lower() == 'yes') and m.author.id == message.author.id
        
        msg = await self.client.wait_for('message', check=check)
        await message.channel.send('You rolled a ' +str(random.randint(1, 6)))

    @commands.command()
    async def unmute(self, ctx, user_id):
        message = ctx.message
        all_channels = message.guild.channels
        member_to_unmute = discord.utils.get(message.guild.members, id=int(user_id))
        if member_to_unmute is not None:
            print("Trying to unmute " + member_to_unmute.name)
            for channel in all_channels:
                perms = channel.permissions_for(member_to_unmute)
                if perms.read_messages and perms.send_messages == False:
                    print("Yes...")
                    await channel.set_permissions(member_to_unmute, send_messages=True)
                else:
                    print("no. they can't read msgs in " + channel.name)
            
            print("Unmuted.")
        else:
            print("Member not found")

        
def setup(bot):
    bot.add_cog(TextCommands(bot))