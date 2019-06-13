import discord
from commands import *
from discord.ext import commands
import courses
import random
from database.database import *

class TextCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.database = load_db('./config/config.json')
    
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
        member_to_unmute = discord.utils.get(message.guild.members, id=int(user_id))
        if member_to_unmute is not None:
            print("Trying to unmute " + member_to_unmute.name)
            muted_role = discord.utils.get(message.guild.roles, name='Muted by Dane')
            if muted_role is not None:
                await member_to_unmute.remove_roles(muted_role, reason="Unmuted by admin.")
            else:
                print("Muted by Dane role was not found.")
        else:
            print("Member not found")

    @commands.command()
    async def mute(self, ctx, user_id, mute_reason):
        message = ctx.message
        member_to_mute = discord.utils.get(ctx.guild.members, id=int(user_id))
        cursor = self.database.cursor()
        cursor.execute("SELECT mute_role FROM Guilds where guild_id = " + str(message.guild.id))
        result = cursor.fetchall()
        mute_role_id = result[0][0]
        if mute_role_id == 0:
            muted_role = await message.guild.create_role(name='Muted by Dane')
            all_channels = message.guild.channels
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages=False
            overwrite.read_messages=True
            for channel in all_channels:
                if channel.permissions_for(message.guild.me).manage_roles: # If the bot can manage permissions for channel, then overrwrite.
                    await channel.set_permissions(muted_role, overwrite=overwrite)

            cursor.execute('UPDATE Guilds SET mute_role = ' + str(muted_role.id) + ' WHERE guild_id = ' + str(message.guild.id))
            self.database.commit()
            await member_to_mute.add_roles(muted_role, reason=mute_reason)
        else:
            role = discord.utils.get(message.guild.roles, id=mute_role_id)
            if role is not None:
                print(role)
                await member_to_mute.add_roles(role, reason="User was spamming.")
            


def setup(bot):
    bot.add_cog(TextCommands(bot))