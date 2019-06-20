import discord
from discord.ext import commands
from utilities.utils import *
import json
from Exceptions.EmbedException import *

class HelpMessageConfigurable(commands.Cog):
    def __init__(self, client):
        self.client=client
        self.database=self.client.database

    '''
        Notes:
            If the admin issues this command, check if their record exists in the GuildHelpMsg table. If it doesn't, insert them with default help_msg {}
    '''

    @commands.group() # Set the Help command to a group. 
    async def help(self, ctx):

        if ctx.invoked_subcommand is None:
            embed=discord.Embed()
            cursor = self.database.cursor()
            cursor.execute("SELECT help_msg, title, color FROM GuildHelpMsg WHERE guild_id=" + str(ctx.guild.id))
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
                    msg = result[0][0]
                    title = result[0][1] if result[0][1] is not None else ''
                    icon_url="https://cdn.discordapp.com/icons/{}/{}.png".format(ctx.guild.id, ctx.guild.icon)
                    embed.title=title
                    embed.set_author(name=ctx.guild.name, icon_url=icon_url)
                    embed.description=json.loads(result[0][0])['msg']
                    embed.color=int(result[0][2])
                    await ctx.channel.send(embed=embed)
        
    @help.command() # sethelp is part of the 'help' group command. This command is used to set the help message.
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
                            help_msg = json.dumps(json_msg).encode('unicode_escape').decode('utf-8')
                            msg_value = json.dumps(json_msg['msg'])  # Dump the JSON to preserve the newline characters
                            print(msg_value)
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
    @help.command()
    @commands.has_permissions(administrator=True)
    async def settitle(self, ctx, *, arg):
        try:
            if len(arg) > 256:
                raise EmbedTitleError("Title cannot exceed 256 characters.")
            cursor = self.database.cursor()
            cursor.execute("SELECT help_msg FROM GuildHelpMsg WHERE guild_id=" + str(ctx.guild.id))
            result = cursor.fetchall()
            empty = {
                "msg" : "Set your help message!"
            }
            print("Guild does not exist. Add them with defaults.")
            values = (str(ctx.guild.id), str(arg), json.dumps(empty), arg)
            cursor.execute("INSERT INTO `GuildHelpMsg` (`guild_id`, `title`, `help_msg`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE title=%s", values)
            embed=discord.Embed()
            embed.description='You set the title to {}'.format(arg)
            await ctx.channel.send(embed=embed)
        except Exception as error:
            if isinstance(error, EmbedTitleError):
                embed=discord.Embed()
                embed.title='Embed Title Characters Limit'
                embed.description='Embed titles cannot exceed 256 characters.'
                await ctx.channel.send(embed=embed)
            else:
                print(error)
    @help.command()
    @commands.has_permissions(administrator=True)
    async def setcolor(self, ctx, color):
        color=int(color, 16)
        try:
            print(color)
            if color >= pow(2,24):
                raise EmbedColorExcepton("Hexadecimal number is out of range!")
            cursor=self.database.cursor()
            values=(str(ctx.guild.id), color, json.dumps({ 'msg': 'Set your message!'}), color)
            cursor.execute("INSERT INTO `GuildHelpMsg` (`guild_id`, `color`, `help_msg`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE color=%s", values)
            embed=discord.Embed()
            embed.description='You set the embed color.'
            await ctx.channel.send(embed=embed)
        except Exception as error:
            if isinstance(error, EmbedColorExcepton):
                embed=discord.Embed()
                embed.title='Hex Color Error'
                embed.description='Hex color code is out of range!'
                await ctx.channel.send(embed=embed)
            else:
                print(error)
        # Check if color entered was a Hexadecimal Value.

def setup(bot):
    bot.add_cog(HelpMessageConfigurable(bot))