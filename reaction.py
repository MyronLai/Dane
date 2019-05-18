import discord
from discord.ext import commands

class ReactionBot(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print('????')
        if payload.message_id == 533900036917166090:
            print(payload.emoji.name)
            # Find a role corresponding to the Emoji name.
            
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g : g.id == guild_id, self.client.guilds)

            channel_id = payload.channel_id
            channel = discord.utils.get(guild.channels, id=channel_id)

            print(channel.name)

            message_id = payload.message_id
            message = await channel.fetch_message(message_id)

            role = discord.utils.find(lambda r : r.name == payload.emoji.name, guild.roles)

            if role is not None:
                print(role.name + " was found!")
                print(role.id)
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                await member.add_roles(role)
                print("done")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id == 533900036917166090:
            print(payload.emoji.name)

            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g : g.id == guild_id, self.client.guilds)
            role = discord.utils.find(lambda r : r.name == payload.emoji.name, guild.roles)

            if role is not None:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                await member.remove_roles(role)
                print("done")

def setup(bot):
    bot.add_cog(ReactionBot(bot))