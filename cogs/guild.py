import discord
from discord.ext import commands
import datetime
from database.keywords import SQLKeywords, SQLTables


class GuildUpdateEvents(commands.Cog):
    def __init__(self, client):
        self.client=client
        self.database=self.client.database

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        cursor = self.database.cursor()
        date = str(guild.created_at)
        values = (str(guild.id), str(guild.owner_id), guild.name, len(guild.members), date)\
            
        try:    
            query = "INSERT INTO " + SQLTables.GUILDS.value + " VALUES "  + str(values)
            cursor.execute(query)
            query = SQLKeywords.INSERT.value + " " + SQLTables.CONFIGURABLES.value + " (guild_id) VALUES ("  + str(guild.id) + ")"
            cursor.execute(query)
        except Exception as error:
            print(error)
        finally:
            cursor.close()
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        
        cursor=self.database.cursor()
        try:
            query="DELETE FROM GuildConfigurables WHERE guild_id=" +str(guild.id)
            cursor.execute(query)
            query="DELETE FROM Guilds WHERE guild_id="+str(guild.id)
            cursor.execute(query)
        except Exception as error:
            print(error)
        finally:
            cursor.close()

def setup(bot):
    bot.add_cog(GuildUpdateEvents(bot))