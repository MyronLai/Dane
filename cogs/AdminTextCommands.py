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

    @commands.command()
    async def setmuterole():
        pass

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
    bot.add_cog(AdminTextCommands(bot))