import discord
from discord.ext import commands
from utils import *
class AdminTextCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.database = self.client.database

    '''
    Command: Prune
    mass delete messages using TextChannel.purge() function, must ensure that the command is issued by an Administrator, and that the user id provided is not of an Admin on the server.
    '''
    @commands.command()
    async def prune(self, ctx, *args):
        if len(args) == 1:
            if ctx.channel.permissions_for(ctx.author).administrator:
                flag = False
                await prune_messages(ctx.message, int(args[0]), flag)
        elif len(args) == 0:
            await prune_messages(ctx.message)
    '''
    Command: setmuterole
        allows the server admin to change the role to give to users when they should not be allowed to send messages. 

        NOTE: Admins are responsible for ensuring permissions are set for each channel. This gives admins the flexibility to decide which channels a user should be able to send messages in, and which channels they can only read messages.
    '''
    @commands.command()
    async def setmuterole(self, ctx, role_id):
        message = ctx.message
        muted_role = discord.utils.find(lambda role: role.id==int(role_id), ctx.guild.roles)
        if muted_role is not None:
            cursor = self.database.cursor()
            cursor.execute("UPDATE Guilds SET mute_role = " + str(role_id) + " WHERE guild_id = " + str(ctx.guild.id))
            self.database.commit()
            embed=discord.Embed()
            embed.title = 'Sucess'
            embed.description= 'You set the mute role to '+ muted_role.mention + '. Users who are muted will be given this role. Please make sure to manually override any channel permissions.'
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("The role with id " + str(role_id) + " was not found! Please try again.")


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
        embed = discord.Embed()
        if member_to_mute is not None:
            mute_role = discord.utils.find(lambda role: role.name=='Muted by Dane', ctx.guild.roles)
            
            cursor = self.database.cursor()
            cursor.execute("SELECT mute_role FROM Guilds WHERE guild_id = " + str(ctx.guild.id))
            result = cursor.fetchall()[0][0]
            if result is None or result == 0:
                print("No")
                embed.title='No Mute Role Set'
                embed.description='Please set a mute role. ?setmuterole <role_id>'
                await message.channel.send(embed=embed)
            else:
                # Mute role is set Check to see if the role is valid
                role = discord.utils.get(ctx.guild.roles, id=int(result))
                if role is not None:
                    await member_to_mute.add_roles(role, reason=mute_reason)
                else:
                    embed.title='Role was not found!'
                    embed.description='The mute role set was not found. Please modify this by setting a new existing role'
                    await message.channel.send(embed=embed)
        else:
            embed.title='Error. Member not found'
            embed.description='Member with id ' + str(user_id) + ' was not found. Please try again'
            await message.channel.send(embed=embed)

    '''
    Command: Ban
    admin command to ban users
    '''
    @commands.command()
    async def ban(self, ctx, user_id, reason):
        await assignUserBan(ctx, user_id, reason)
    
    @commands.command()
    async def kick(self, ctx, user_id, reason):
        await kickUser(ctx, int(user_id), reason)
        
def setup(bot):
    bot.add_cog(AdminTextCommands(bot))