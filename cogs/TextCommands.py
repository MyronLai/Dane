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
    async def subscribe(self, ctx, channel_type, *args):
        if len(args) == 0:
            embed=discord.Embed()
            if channel_type.lower() == 'voice':
                embed.title='List of all Voice Channels and their IDs'
                embed.color=5904098
                description=''
                embed.set_footer(text='Enter the ID of the voice channel you wish to subscribe to.', icon_url='https://cdn2.iconfinder.com/data/icons/metro-uinvert-dock/256/Microphone_1.png')
                voice_channels=ctx.guild.voice_channels
                for channel in voice_channels:
                    description += "**Channel:** " + channel.name +  " **ID:** " + "__" + str(channel.id) + "__\n"
                embed.description=description
                embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
                await ctx.channel.send(embed=embed)
                
                def check(msg):
                    try:
                        return msg.author.id == ctx.author.id and discord.utils.get(voice_channels, id=int(msg.content)) is not None
                    except Exception as error:
                        print(error)

                user_response = await self.client.wait_for('message', check=check)
                print(user_response.content)
            elif channel_type.lower() == 'text':
                pass
        else:
            pass



def setup(bot):
    bot.add_cog(TextCommands(bot))