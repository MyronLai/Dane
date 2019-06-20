import discord
from discord.ext import commands
from utilities.utils import *
import json
class HelpMessageConfigurable(commands.Cog):
    def __init__(self, client):
        self.client=client
        self.database=self.client.database

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
    
def setup(bot):
    bot.add_cog(HelpMessageConfigurable(bot))