import discord
from discord.ext import commands
from database.dbutils import *
import re

class SubscriptionCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.database = self.client.database
    @commands.command()
    async def subbed(self, ctx): # Show all channels the user is subscribed to   
        channels = await get_subscribed_channels(ctx.author.id, self.client.database)
        embed=discord.Embed()
        embed.title='Subscribed Channels'
        embed.set_author(name="{}#{}".format(ctx.author.name, ctx.author.discriminator), icon_url=ctx.author.avatar_url)
        if channels is not None:
            voice_channel_list = []
            for channel in channels:
                res = discord.utils.get(ctx.guild.voice_channels, id=int(channel[0]))
                if res is not None:
                    voice_channel_list.append(res)
            description = ''
            for channel in voice_channel_list:
                description += "**Channel:** {} **ID:** {}\n".format(channel.name, channel.id)
            
            embed.description=description
            embed.color=1733275
            await ctx.channel.send(embed=embed)
        else:
            embed.description='You are not subscribed to any channels.'
            embed.color=1733275
            await ctx.channel.send(embed=embed)
    @commands.command()
    async def sub(self, ctx, *args):
        voice_channels=ctx.guild.voice_channels
        embed=discord.Embed()
        if len(args) == 0:
            embed.title='List of all Voice Channels and their IDs'
            embed.color=5904098
            description=''
            embed.set_footer(text='Enter the ID of the voice channel you wish to subscribe to.', icon_url='https://cdn2.iconfinder.com/data/icons/metro-uinvert-dock/256/Microphone_1.png')
            for channel in voice_channels:
                description += "**Name:** " + channel.name +  " - **ID:** " + "__" + str(channel.id) + "__\n"
            embed.description=description
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            await ctx.channel.send(embed=embed)
            
            def check(msg):
                try:
                    return msg.author.id == ctx.author.id and discord.utils.get(voice_channels, id=int(msg.content)) is not None
                except Exception as error:
                    print(error)

            response = await self.client.wait_for('message', check=check)
            # Now subscribe the user to the database.
            await subscribe_user(response.content, ctx, self.database)
                
        else: # This case is for Users that call the command with specified voice channel ids
            def filter_ids(iter): # Filter function to filter out all invalid Voice Channel Ids
                if discord.utils.find(lambda channel:channel.id==int(iter), voice_channels) is not None:
                    return True
                else:
                    return False
            valid_channel_ids = list(filter(filter_ids, args))
            try:
                #voice_channels = map(lambda c : c.name, voice_channels)
                voice_channels  = [] # This is a list of all the valid voice channels the user was trying to subscribe to.
                for id in valid_channel_ids:
                    channel = discord.utils.get(ctx.guild.voice_channels, id=int(id))
                    if channel is not None:
                        voice_channels.append(channel)

                desc='\n'
                for voice in voice_channels:
                    desc += "{} ({})\n".format(voice.name, voice.id)
                await subscribe_user(valid_channel_ids, ctx, self.client.database)
                embed.set_author(name="{}#{}".format(ctx.author.name, ctx.author.discriminator), icon_url=ctx.author.avatar_url)
                embed.description="{} was subscribed to:\n{}".format(ctx.author.mention, desc)
                embed.set_footer(text='To unsubscribe, use ?unsubscribe <channel_id>')
                embed.color=2342399
                await ctx.channel.send(embed=embed)
                
            except Exception as error:
                print(error)

    @commands.command()
    async def unsub(self, ctx, channel_id):
        voice_channels=map(lambda channel: channel.id, ctx.guild.voice_channels)
        try:
            if int(channel_id) in voice_channels: # If id passed in by user is a valid voice channel...
                await unsubscribe_user(channel_id, ctx, self.client.database)

        except Exception as error:
            print("Hi")
            print(error)

    @commands.command()
    async def wl(self, ctx, *args): # Args should only contain the channel id.
        cursor = self.database.cursor()
        embed=discord.Embed()
        if len(args) != 0:
            channel = discord.utils.find(lambda c : c.id==int(args[0]), ctx.guild.voice_channels)# Check if Channel is not None
            if channel is not None:
                for member in ctx.message.mentions:
                    if member.id != ctx.author.id:
                        cursor.execute("SELECT * FROM VoiceChannelWhitelist WHERE client_id={} AND channel_id={} AND whitelisted_user={}".format(str(ctx.author.id),str(channel.id), str(member.id)))
                        result = cursor.fetchall()
                        if len(result) == 0:# Insert record
                            cursor.execute("INSERT INTO VoiceChannelWhitelist VALUES ({}, {}, {}, {}, {})".format(str(channel.id), str(ctx.guild.id), str(ctx.author.id), str(member.id), 1))
                            print('done')
                        else: # Record Exists. Set the field isWhitelisted to 1
                            cursor.execute("UPDATE VoiceChannelWhitelist SET isWhitelisted=1 WHERE client_id={} AND channel_id={} AND whitelisted_user={}".format(str(ctx.author.id),str(channel.id), str(member.id)))
                            print("Updated.")
                    else:
                        print("Cannot whitelist self!")
                # Send an embed message telling users who they waitlisted successfully.
            else:
                embed.description="Channel was not found"
                await ctx.channel.send(embed=embed)
        else: # Need to list the white list for channels ONLY if they are subscribed.
            cursor.execute("SELECT channel_id, whitelisted_user FROM VoiceChannelWhitelist WHERE guild_id={} AND client_id={} AND isWhitelisted=1".format(str(ctx.guild.id), str(ctx.author.id)))   
            result=cursor.fetchall() # This will return a  list of tuples that contain the whitelisted user, and the channel.
            whitelist = {}
            for row in result: # Loop through each row from the result set.
                member = discord.utils.find(lambda m: m.id==int(row[1]), ctx.guild.members)
                if row[0] in whitelist and member is not None: # Check if row[0], (the channel id) is in the dictionary.
                    whitelist[row[0]].append(member) # If it is, add row[1] (the whitelisted user) to the dictionary's array
                elif member is not None:
                    whitelist[row[0]] = [member]
            # So all of the records from the  DB is correct. We have a bug with this for loop.
            description=''
            for channel_id in whitelist:
                channel = discord.utils.find(lambda c: c.id==int(channel_id), ctx.guild.voice_channels)
                subscribed_users = whitelist[channel_id]
                #description+="__**Channel:**__ {}\n**Id: **{}\n\n".format(channel.name, str(channel.id))
                for user in subscribed_users:
                    description += user.mention + "\n"
                embed.add_field(name=channel.name + "\n" + str(channel.id), value=description,inline=True)
                description=''
            icon_url="https://cdn.discordapp.com/icons/{}/{}.png".format(ctx.guild.id, ctx.guild.icon)
            embed.set_thumbnail(url=icon_url)
            embed.set_author(name="{}#{}'s Voice Channel Whitelist".format(ctx.author.name, str(ctx.author.discriminator)), icon_url=ctx.author.avatar_url)
            embed.color=1900482
            embed.set_footer(text='To whitelist someone, first subscribe to a channel, and then issue the command: e.g: ?wl 582319490604335107 @UserToWhitelist#1337')
            
            await ctx.channel.send(embed=embed)

    '''
        COMMAND: CLEAR WHITELIST ?clearwl
        Clears the user's whitelist for a given channel. Internally on the server it will set all of their records for 'isSubscribed' to 0.
    '''
    @commands.command()
    async def clearwl(self, ctx, channel_id):
        channel = discord.utils.find(lambda c: c.id==int(channel_id), ctx.guild.channels)
        try:
            if channel is not None:
                cursor = self.database.cursor()
                cursor.execute("UPDATE VoiceChannelWhitelist SET isWhitelisted = 0 WHERE client_id={} AND channel_id={} AND guild_id={}".format(str(ctx.author.id), str(channel.id), str(ctx.guild.id)))
                embed=discord.Embed()
                embed.description="Cleared {]'s whitelist for {}".format(ctx.author.mention, channel.name)
                await ctx.channel.send(embed=embed)
            else:
                raise Exception("Channel not found.")
        except Exception as error:
            print(error)
    '''
        COMMAND: UNSUBALL ?unsuball
        Unsubs the user from every single channel in the guild where the command was issued. Right now the user's whitelist is not cleared, as they might want to keep it
        for some other time they wish to resubscribe. They will not receive a notification when a user joins a channel, even if they are on the whitelist. This is good!
    '''
    @commands.command()
    async def unsuball(self, ctx):
        cursor = self.database.cursor()
        try:
            cursor.execute("UPDATE VoiceChannelSubscriptions SET isSubscribed=0 WHERE client_id={} AND guild_id={}".format(str(ctx.author.id), str(ctx.guild.id)))
            print('Done')
        except Exception as error:
            print(error)
        finally:
            cursor.close()
    
    @commands.command()
    async def suball(self, ctx):
        cursor = self.database.cursor()
        voice_channels = ctx.guild.voice_channels
        # Subbing 1 User to ALL Channels in the Guild.
        # VALUES (channel_id, guild_id,  client_id, 1)
        values = []
        for vc in voice_channels:
            if vc.permissions_for(ctx.author).connect: #If the user can connect to the channel, they will be subscribed!
                values.append((str(vc.id), str(ctx.guild.id), str(ctx.author.id), 1))

        value_str = ''
        i = 0
        for t in values: # Loop through all values and append the tuple to a string.
            value_str += str(t)
            value_str += "," if i < len(values)-1 else ''  # Ternary Operator to avoid adding a comma at the last value tuple
            i+=1
        
        try:
            cursor.execute("INSERT INTO VoiceChannelSubscriptions (channel_id, guild_id, client_id, isSubscribed) VALUES " +str(value_str) + " ON DUPLICATE KEY UPDATE isSubscribed=1")
        except Exception as error:
            print(error)
def setup(bot):
    bot.add_cog(SubscriptionCommands(bot))