import discord
from discord.ext import commands
from utilities.utils import *
from database.keywords import *
import json

class AdminTextCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.database = self.client.database
        
    '''
    Command: Prune
        mass delete messages using TextChannel.purge() function, must ensure that the command is issued by an Administrator, and that the user id provided is not of an Admin on the server. If no user id is passed, it will purge all messages regardless of the author.

    '''
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prune(self, ctx, user_id, limit):
        try:
            if int(limit) > 250:
                raise Exception("Cannot exceed the limit of 250 messages")
            else:
                msgs = await ctx.channel.purge(limit=int(limit), check=lambda m: m.author.id == int(user_id))
                embed=discord.Embed()
                embed.title='Server Action'
                embed.description='{} messages were deleted.'.format(str(len(msgs)))
                await ctx.channel.send(embed=embed)
        except Exception as error:
            print(error)
    '''
    Command: setmuterole
        allows the server admin to change the role to give to users when they should not be allowed to send messages. 

        NOTE: Admins are responsible for ensuring permissions are set for each channel. This gives admins the flexibility to decide which channels a user should be able to send messages in, and which channels they can only read messages.
    '''
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setmute(self, ctx, role_id): # Messages should go in Mod-Logs.
        message = ctx.message
        muted_role = discord.utils.find(lambda role: role.id==int(role_id), ctx.guild.roles)
        cursor = self.database.cursor()
        if muted_role is not None:
            try:
                cursor.execute("SELECT mute_role FROM GuildConfigurables WHERE guild_id=" + str(ctx.guild.id))
                result = cursor.fetchall()
                if len(result) == 0: # If Guild is not in GuildConfigurables for some reason, give  them defaults.
                    cursor.execute("INSERT INTO GuildConfigurables VALUES({}, DEFAULT, {}, DEFAULT, DEFAULT)".format(str(ctx.guild.id), str(muted_role.id)))
                else:
                    cursor.execute("UPDATE " + SQLTables.CONFIGURABLES.value + " SET mute_role = " + str(muted_role.id) + " WHERE guild_id = " + str(ctx.guild.id))
            except Exception as error:
                print(error)
            finally:
                cursor.close()
                embed=discord.Embed()
                embed.title = 'Sucess'
                embed.description='You set the mute role to '+ muted_role.mention + '. Users who are muted will be given this role. Please make sure to manually override any channel permissions.'
                await message.channel.send(embed=embed)
        else:
            await message.channel.send("The role with id " + str(role_id) + " was not found! Please try again.")
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sethelp(self, ctx): # Messages should go in Bot Logs
        if ctx.channel.permissions_for(ctx.author).administrator:

            # Make sure the Database has the Guild.
            try:
                cursor = self.database.cursor()
                cursor.execute("SELECT * FROM Guilds WHERE guild_id={}".format(str(ctx.guild.id)))
                result = cursor.fetchall()
                if len(result) == 0: # Guild is not in DB!
                    cursor.execute("INSERT INTO Guilds VALUES({}, {}, {}, {}, {}".format(str(ctx.guild.id), str(ctx.guild.owner_id), ctx.guild.name, len(ctx.guild.members), str(ctx.guild.created_at)))
                else:
                    print("Guild is in DB! Continue")
            except Exception as error:
                print(error)
            
            message = ctx.message
            choice = 'yes'
            while choice.lower() == 'yes':
                await message.channel.send("Please enter your message.")
                '''
                    - Filter function. 
                    - Checks if message is from original author.
                    - Checks if the original author's message starts with ``` and ends with ```
                '''
                def check(m): 
                    return m.author == ctx.author and (m.content.startswith("```") and m.content.endswith("```"))
                        
                msg = await self.client.wait_for('message', check=check) 
                msg = parse_help_msg(msg.content) # Parse message
                json_msg = { "msg" : msg } 
                embed=discord.Embed()
                embed.title='Server Help Directory'
                embed.color=13951737
                embed.description=msg
                description_msg=''
                try: # Loop until the user says yes or quit
                    await message.channel.send("Are you sure you want this? Yes/No", embed=embed)
                    '''
                        - Checks if original author.
                        - Checks if the user typed yes/no 
                    '''
                    def check(m):
                        return m.author == ctx.author and (m.content.lower()=='yes' or m.content.lower() =='no')
                    
                    confirm = await self.client.wait_for('message', check=check, timeout=30)
                    if confirm.content.lower() == 'yes': # If they entered yes, save their response to the database.
                        try:
                            print(description_msg)
                            cursor = self.database.cursor() # Use JSON DUMPS to serialize the json dictionary. Encode it to bytes, and decode to utf-8 when storing it as a string.
                            #query = "UPDATE GuildConfigurables SET help_msg='" + json.dumps(json_msg).encode('unicode_escape').decode('utf-8') + "' WHERE guild_id="+(str(ctx.guild.id))
                            help_msg = json.dumps(json_msg).encode('unicode_escape').decode('utf-8')
                            msg_value = json.dumps(json_msg['msg'])  # Dump the JSON to preserve the newline characters
                            cursor.execute("INSERT INTO GuildHelpMsg (guild_id, help_msg) VALUES(" + str(ctx.guild.id) + ",'" + help_msg +"') ON DUPLICATE KEY UPDATE help_msg=JSON_SET(help_msg, \"$.msg\"," +msg_value +")")
                            cursor.close()
                            embed.title='Server Message'
                            embed.description='Success!'
                            embed.color=10747835
                            await message.channel.send(embed=embed)
                        except Exception as error:
                            embed.title='Server Error'
                            embed.description=str(error)
                            embed.color=16724999
                            await message.channel.send(embed=embed)
                        finally:
                            break # Break out of loop once the user says yes.
                    else:
                        await ctx.channel.send("Do you want to try again? Yes/No")
                        choice = await self.client.wait_for('message', check=check) # This will call the check function inside it's try scope.
                        choice = choice.content.lower() # If choice is not yes, it will break the loop.
                except (Exception, asyncio.TimeoutError) as error:
                    print(error)
                    await message.channel.send("Took too long!")
                    break
                
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setmodchannel(self, ctx, channel_id):
        cursor = self.database.cursor()
        cursor.execute("SELECT mod_channel FROM GuildConfigurables WHERE guild_id={}".format(str(ctx.guild.id)))
        result = cursor.fetchall()
        try:
            if len(result) == 0:
                cursor.execute("INSERT INTO GuildConfigurables VALUES({}, DEFAULT, DEFAULT, DEFAULT, {})".format(str(ctx.guild.id), str(channel_id)))
            else:
                cursor.execute("UPDATE GuildConfigurables SET mod_channel={}".format(str(channel_id)))
        except Exception as error:
            print(error)
        
        finally:
            cursor.close()
    '''
        command: unmute

        args:
            user_id (int): The id of the user to unmute
    '''
    @commands.command() # Message should go in Bot Logs
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, user_id):
        message = ctx.message
        user = discord.utils.find(lambda user: user.id==int(user_id), ctx.guild.members)
        embed = discord.Embed()
        if user is not None:
            # Find the role muted role
            cursor = self.database.cursor()
            cursor.execute("SELECT mute_role FROM {} WHERE guild_id={}".format(SQLTables.CONFIGURABLES.value, str(ctx.guild.id)))
            result = cursor.fetchall()[0][0]

            if result is None or result == 0:
                embed.title='Error : Mute role is not set!'
                embed.description='Please set the mute role. ?setmuterole <role_id>'
                await message.channel.send(embed=embed)
            else:
                mute_role = discord.utils.get(ctx.guild.roles, id=int(result))
                if mute_role is not None:
                    await user.remove_roles(mute_role)
                    embed.title='Server Action'
                    embed.description=user.mention + ' (' + str(user_id) + ') was unmuted!'
                    await message.channel.send(embed=embed)
                else:
                    print("Mute role not found")
        else:
            embed.title='Error : User was not found'
            embed.description='The user with id ' + str(user_id) + ' was not found'
            await message.channel.send(embed=embed)
    '''
        command: mute

        args: 
    '''
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, user_id, mute_reason):
        message = ctx.message
        member_to_mute = discord.utils.get(ctx.guild.members, id=int(user_id))
        embed = discord.Embed()
        if member_to_mute is not None:
            
            cursor = self.database.cursor()
            cursor.execute("SELECT mute_role FROM {} WHERE guild_id = {}".format(SQLTables.CONFIGURABLES.value, str(ctx.guild.id)))
            result = cursor.fetchall()[0][0]
            print(result)
            if result is None or result == 0:
                print("No")
                embed.title='No Mute Role Set'
                embed.description='Please set a mute role. ?setmuterole <role_id>'
                await message.channel.send(embed=embed)
            else:
                print("Role found")
                # Mute role is set Check to see if the role is valid
                role = discord.utils.get(ctx.guild.roles, id=int(result))
                if role is not None:
                    await member_to_mute.add_roles(role, reason=mute_reason)
                    embed.title='Success'
                    embed.description=member_to_mute.mention + ' was muted.'
                    await message.channel.send(embed=embed)
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
            Bans a GuildMember from the Guild

            args:
            user_id (int) : - The id of the Guild Member to ban
            reason (string) : - Reason of the ban3
    '''
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user_id, reason):
        user = discord.utils.get(ctx.guild.members, id=int(user_id))
        if user is not None:
            if ctx.author.id == ctx.guild.owner_id: # If the command was triggered by the Owner
                await ctx.guild.ban(user, delete_message_days=1, reason=reason)
            elif ctx.channel.permissions_for(user).ban_members:
                print("Bot cannot ban another mod/user with ban_members permissions")
            else:
                await ctx.guild.ban(user, delete_message_days=1, reason=reason)
        else:
            print('Non-Admin trying to issue a ban')
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id):
        banned_users = await ctx.guild.bans()
        user = discord.utils.find(lambda ban: ban.user.id==int(user_id), banned_users).user
        await ctx.guild.unban(user)
        print("Unbanned")
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user_id, reason):
        await kickUser(ctx, int(user_id), reason)
        
def setup(bot):
    bot.add_cog(AdminTextCommands(bot))