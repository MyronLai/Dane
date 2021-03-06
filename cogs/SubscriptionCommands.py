import discord
from discord.ext import commands
from database.dbutils import *
import re
import datetime
from utilities  import utils

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
            
            '''
                This filter validates the voice channel for us.
            '''
            def check(msg):
                try:
                    return msg.author.id == ctx.author.id and discord.utils.get(voice_channels, id=int(msg.content)) is not None
                except Exception as error:
                    print(error)

            try:
                response = await self.client.wait_for('message', check=check)
                # Now subscribe the user to the database.
                await subscribe_user(response.content, ctx, self.database)
                channel = discord.utils.get(voice_channels, id=int(response.content))
                embed.title='Success!'
                embed.description=ctx.author.mention + ' was subscribed to ' + channel.name
                await ctx.channel.send(embed=embed)
            except Exception as error:
                print(error)
                
        else: # This case is for Users that call the command with specified voice channel ids
            def filter_ids(iter): # Filter function to filter out all invalid Voice Channel Ids
                return True if discord.utils.find(lambda channel:channel.id==int(iter), voice_channels) else False
                
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
            print(error)

    @commands.command()
    async def wl(self, ctx, *args): # Args should only contain the channel id.
        cursor = self.database.cursor()
        embed=discord.Embed()
        if len(args) != 0:
            channel = discord.utils.find(lambda c : c.id==int(args[0]), ctx.guild.voice_channels)
            if channel is not None: 
                for member in ctx.message.mentions:
                    try:
                        if member.id != ctx.author.id:
                            await subscribe_user(channel.id, ctx, self.database) # Sub the user
                            cursor.execute("SELECT * FROM VoiceChannelWhitelist WHERE client_id={} AND channel_id={} AND whitelisted_user={}".format(str(ctx.author.id),str(channel.id), str(member.id)))
                            result = cursor.fetchall()
                            if len(result) == 0:# Insert record if they were not found.
                                cursor.execute("INSERT INTO VoiceChannelWhitelist VALUES ({}, {}, {}, {}, {})".format(str(channel.id), str(ctx.guild.id), str(ctx.author.id), str(member.id), 1))
                                print('done')
                            else: # Record Exists. Set the field isWhitelisted to 1
                                cursor.execute("UPDATE VoiceChannelWhitelist SET isWhitelisted=1 WHERE client_id={} AND channel_id={} AND whitelisted_user={}".format(str(ctx.author.id),str(channel.id), str(member.id)))
                                print("Updated.")
                        else:
                            print("Cannot whitelist self!")
                    except Exception as error:
                        print(error)
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
        Clearing a whitelist does not unsubscribe you from the channel.

    '''
    @commands.command()
    async def clearwl(self, ctx, channel_id):
        channel = discord.utils.find(lambda c: c.id==int(channel_id), ctx.guild.channels)
        try:
            if channel is not None:
                cursor = self.database.cursor()
                cursor.execute("UPDATE VoiceChannelWhitelist SET isWhitelisted=0 WHERE client_id={} AND channel_id={} AND guild_id={}".format(str(ctx.author.id), str(channel.id), str(ctx.guild.id)))
                embed=discord.Embed()
                embed.description="Cleared {}'s whitelist for {}".format(ctx.author.mention, channel.name)
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
            await ctx.invoke(self.client.get_command('subbed'))
        except Exception as error:
            print(error)
        finally:
            cursor.close()
    '''
        SOME NOTES:
            If a user is subscribed to some channels and uses ?suball, the Database will just insert them and set isSubscribed to 1.
    '''
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
            await ctx.invoke(self.client.get_command('subbed')) #Invoke te sub command which displays all subbed channels
        except Exception as error:
            print(error)
        '''
        - If a User does not have a whitelist, then they will receive  notifications for ALL members that join.
        - If a User's whitelist contains at least one user, then we will only send notifications when that user joins.
        - If a User is in a Voice Channel, and another user joins a voice channel that is in the same Guild and is also on the user's whitelist, the user will NOT be notified
        - If a User is in a Voice Channel on another Guild, and someone joins a voice channel in another Guild that the User is also subscribed to, they will receive a notification if that person who joined is on the whitelist.
    '''
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if before.channel is None and after.channel is not None: # User joins a Voice Channel while not being in one.
            cursor = self.database.cursor()
            # This query will give us ALL of the Clients that are subscribed to the voice channel some user just joined.
            cursor.execute("SELECT client_id FROM VoiceChannelSubscriptions WHERE channel_id={} AND isSubscribed={}".format(str(after.channel.id), 1))
            result = cursor.fetchall()
            for id in result: # Loop through each id in the result set. Each ID represents the client subscribed.
                current_member = discord.utils.find(lambda m: m.id==int(id[0]), member.guild.members) # Check if the Member exists in Guild.
                if current_member is not None and current_member.id != member.id: # If member is not none, and also not the  person who joined.
                    # We need to get the CLIENT's whitelist and check if the member who joined is in the whitelist.
                    cursor.execute("SELECT whitelisted_user FROM VoiceChannelWhitelist WHERE channel_id={} AND client_id={} AND isWhitelisted={} AND isWhitelisted=1".format(str(after.channel.id), str(current_member.id), 1)) # Select whitelisted_user column, if the MEMBER who joined is in the whitelist, then we send a message.
                    print("A user joined. Showing whitelist for " + str(current_member) + " " + str(current_member.id))
                    result = cursor.fetchall()
                    embed=discord.Embed()
                    embed.set_author(name=member.name,icon_url=member.avatar_url)
                    embed.description="{} joined {} in {}".format(member.name, after.channel.name, member.guild.name)
                    embed.set_footer(text=str(datetime.datetime.now().strftime("%A - %B %d at %I:%M:%S %p")))

                    if len(result) != 0: # If the user's whitelist is not empty
                        ids = map(lambda n : n[0], result)
                        if member.id in ids and current_member.voice is None: # Check if the member id is in the whitelist.
                            print("Sending message...." + member.name + " is in the whitelist.")
                            #utils.isNotified(current_member.id, member.id)
                            await current_member.send(embed=embed)
                        else:
                            print(member.name + " is not in the whitelist for " + current_member.name + " or they are in a voice channel.")
                    else: # If their whitelist is empty, send.
                        ids = map(lambda n : n[0], result)
                        if current_member.voice is None:
                            #utils.isNotified(current_member.id, member.id)
                            await current_member.send(embed=embed)
        
        elif before.channel is not None and after.channel is not None:

            if before.channel.id != after.channel.id:
                print("User Switched.") 
                cursor = self.database.cursor()
                cursor.execute("SELECT client_id FROM VoiceChannelSubscriptions WHERE channel_id={} AND isSubscribed={}".format(str(after.channel.id), 1))
                result = cursor.fetchall()
                print(result)
                for id in result: # Loop through each id in the result set. Each ID represents the client subscribed.
                    current_member = discord.utils.find(lambda m: m.id==int(id[0]), member.guild.members) # Check if the  Member exists in Guild.
                    if current_member is not None and current_member.id != member.id: # If member is not none, and also not the  person who joined.
                        # We need to get the CLIENT's whitelist and check if the member who joined is in the whitelist.
                        cursor.execute("SELECT whitelisted_user FROM VoiceChannelWhitelist WHERE channel_id={} AND client_id={} AND isWhitelisted={} AND isWhitelisted=1".format(str(after.channel.id), str(current_member.id), 1)) # Select whitelisted_user column, if the MEMBER who joined is in the whitelist, then we send a message.
                        result = cursor.fetchall()

                        embed=discord.Embed()
                        embed.set_author(name=member.name,icon_url=member.avatar_url)
                        embed.description="{} joined  {} in {}".format(member.name, after.channel.name, member.guild.name)
                        embed.set_footer(text=str(datetime.datetime.now().strftime("%A - %B %d at %I:%M:%S %p")))
                        
                        if len(result) != 0: # If the user's whitelist is not empty
                            ids = map(lambda n : n[0], result)
                            if member.id in ids and current_member.voice is None: # Check if the member id is in the whitelist.
                                await current_member.send(embed=embed)
                            
                        else: # If their whitelist is empty, send.
                            if current_member.voice is None:
                                await current_member.send(embed=embed)
            else:
                print("User changed their voice state.")

        elif before.channel is not None and after.channel is None:
            print("user left")
def setup(bot):
    bot.add_cog(SubscriptionCommands(bot))