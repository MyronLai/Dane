import discord
from utils import *
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
        mute_role = discord.utils.find(lambda role: role.name=='Muted by Dane', ctx.guild.roles)

        try:
            if mute_role is not None:
                print("Muting user.")
                await member_to_mute.add_roles(mute_role, reason="Muted by admin")
            else:
                print("Role does not exist.")
        except Exception as err:
            print(err)

    @commands.command()
    async def sethelpcmd(self, ctx):
        if ctx.channel.permissions_for(ctx.author).administrator:
            message = ctx.message
            await message.channel.send("Please enter your message. To separate lines, make sure to add a \\n.")
            def check(m):
                return (m.author == ctx.author) or (m.author == ctx.author and m.content == 'yes')
            
            msg = await self.client.wait_for('message', check=check)
            array = msg.content.split("\\n")
            description_msg = ''
            for line in array:
                description_msg += line + '\n'
            embed=discord.Embed()
            embed.title='Server Help Directory'
            embed.description=description_msg
            embed.color=13951737

            try:
                await message.channel.send("Are you sure you want this?", embed=embed)
                confirm = await self.client.wait_for('message', check=check,timeout=10)
                try:
                    print(description_msg)
                    cursor = self.database.cursor()
                    query = "UPDATE Guilds SET help_msg=\""+description_msg+"\" WHERE guild_id="+(str(ctx.guild.id))
                    print(query)
                    cursor.execute(query)
                    self.database.commit()
                    embed.title='Server Message'
                    embed.description='Success!'
                    embed.color=10747835
                    await message.channel.send(embed=embed)
                except Exception as error:
                    embed.title='Server Error'
                    embed.description=str(error)
                    embed.color=16724999
                    await message.channel.send(embed=embed)
            except asyncio.TimeoutError:
                await message.channel.send("Took too long!")
            
        else:
            print("Not an admin.")

def setup(bot):
    bot.add_cog(TextCommands(bot))