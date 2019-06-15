import discord
from discord.ext import commands
import datetime

class GuildUpdateEvents(commands.Cog):
    def __init__(self, client):
        self.client=client
        self.database=self.client.database

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(guild.id)
        cursor = self.database.cursor()
        cursor.execute("INSERT INTO Guilds VALUES(" + str(guild.id) + ", DEFAULT, DEFAULT, DEFAULT)")
        self.database.commit()
        print("Done.")
        # Every Guild needs a mod-logs channel, mute role
        dane_logs_channel = discord.utils.get(guild.channels, name='dane-logs')
        if dane_logs_channel is not None:
            embed = discord.Embed()
            embed.title = 'Dane Bot Joined ' + guild.name
            embed.description = 'Dane Bot automatically looks for the channel dane-logs and keeps all mod and error messages in there.'
            await dane_logs_channel.send(embed=embed)
        else:
            # Create Dane Log Channel.
            pass

def setup(bot):
    bot.add_cog(GuildUpdateEvents(bot))