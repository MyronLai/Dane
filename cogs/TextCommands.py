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
    async def subscribe(self, ctx, *args):
        if len(args) == 0:
            print("No params.")
            return
        else:
            role = discord.utils.find(lambda role: role.name=='Subscribe', ctx.guild.roles)
            args = ''.join(args)
            voice_channel_ids = args.split(",")
            user_id = ctx.author.id
            cursor = self.database.cursor()

            for voice_id in voice_channel_ids:
                print("voice id  = " + str(voice_id))
                jsonArray = "'[\"" + str(ctx.author.id) + "\"]'"
                cursor.execute("SELECT channel_id, users_subscribed FROM ChannelSubscriptions WHERE channel_id = " + str(voice_id))
                result = cursor.fetchall()
                print(result)
                if len(result) == 0:
                    print('hello')
                    cursor.execute("INSERT INTO ChannelSubscriptions VALUES(" + str(voice_id) + ", " + jsonArray + ")")
                else:
                    print("the channel exists. append user")
                    users_str = json.loads(result[0][1])
                    print(users_str)
                    if str(ctx.author.id) in users_str:
                        print("User is already subscribed!")
                    else:
                        users_str.append(str(ctx.author.id))
                        print(users_str)

                    users_str = json.dumps(users_str)
                    print("DATA: " + str(users_str))
                    cursor.execute("UPDATE ChannelSubscriptions SET users_subscribed = '" + str(users_str) + "'")
                    
                    print('done?')

            ''' voice_channels = []
            for channel_id in voice_channel_ids:
                channel = discord.utils.find(lambda c: c.id==int(channel_id), ctx.guild.channels)
                voice_channels.append(str(channel.id))
                print("Added " + str(channel.name))
            
            cursor = self.database.cursor()
            cursor.execute("SELECT channels FROM Subscriptions WHERE client_id=" + str(ctx.author.id) + " AND guild_id="+str(ctx.guild.id))
            result = cursor.fetchall()
            print(result)

            if len(result) == 0:
                channels = ','.join(voice_channels)
                print(channels)
                cursor.execute("INSERT INTO Subscriptions VALUES(" + str(ctx.guild.id) + "," + str(ctx.author.id) + ",'" + str(channels) + "')")
                print("Done")
            else:
                pass
            embed=discord.Embed()
            if role is not None:
                await ctx.author.add_roles(role)
                embed.description='Subscribed!'
                await ctx.channel.send(embed=embed)
            else:
                embed.description='Role does not exist'
                await ctx.channel.send(embed=embed)
            else:
                embed.title='Error'
                embed.description='The role with id ' + int(voice_channel_id) + ' does not exist!'
                await ctx.channel.send(embed=embed)'''




def setup(bot):
    bot.add_cog(TextCommands(bot))