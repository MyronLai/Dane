
async def subscribe_user(channel_id, ctx, database):
    cursor = database.cursor() # Need to query database and check if User Exists in the VoiceChannelSubscriptions Table
    if type(channel_id) != list: # If user_id is not a list, then only one parameter was passed in as a str/int.
        try:
            cursor.execute("SELECT * FROM VoiceChannelSubscriptions WHERE client_id=" + str(ctx.author.id) + " AND channel_id=" + str(channel_id))
            results = cursor.fetchall()
            if len(results) == 0: # Insert the  user into the database, set isSubscribed to 1.
                cursor.execute("INSERT INTO VoiceChannelSubscriptions VALUES({}, {}, {}, {})".format(channel_id, ctx.guild.id, ctx.author.id, 1))
            else:
                cursor.execute("UPDATE VoiceChannelSubscriptions SET isSubscribed=1 WHERE client_id={} AND channel_id={}".format(ctx.author.id, channel_id))
        except Exception as error:
            print(error)
        
    else: # Loop through the list and append each user/set their status to isSubscribed = 1.
        try:
            for id in channel_id:
                cursor.execute("SELECT * FROM VoiceChannelSubscriptions WHERE client_id=" + str(ctx.author.id) + " AND channel_id=" + str(id))
                result = cursor.fetchall()
                if len(result) == 0:
                    cursor.execute("INSERT INTO VoiceChannelSubscriptions VALUES({}, {}, {}, {})".format(id, ctx.guild.id, ctx.author.id, 1))
                else:
                    cursor.execute("UPDATE VoiceChannelSubscriptions SET isSubscribed=1 WHERE client_id=" + str(ctx.author.id) +  " AND channel_id=" + str(id))
                    print("????")
        except Exception as error:
            print(error)

    cursor.close()

''' Returns all channnels the user is subscribed to as a tuple'''
async def get_subscribed_channels(user_id, database):
    cursor = database.cursor()
    cursor.execute("SELECT channel_id FROM VoiceChannelSubscriptions WHERE client_id=" + str(user_id) + " AND isSubscribed=1")
    result = cursor.fetchall()
    return result if len(result) != 0 else None

async def unsubscribe_user(channel_id, ctx, database):
    cursor = database.cursor()
    if type(channel_id) != list:
        try:
           # cursor.execute("INSERT INTO VoiceChannelSubscriptions VALUES({},{},{},{}) ON DUPLICATE KEY UPDATE isSubscribed=0".format(str(channel_id), str(ctx.guild.id), str(ctx.author.id), 0))
            cursor.execute("SELECT isSubscribed FROM VoiceChannelSubscriptions WHERE channel_id=" + str(channel_id))
            result = cursor.fetchall()
            if len(result) != 0:
                isSubscribed=result[0][0]
                print(isSubscribed)
                if isSubscribed==1:
                    cursor.execute("UPDATE VoiceChannelSubscriptions SET isSubscribed=0 WHERE client_id=" + str(ctx.author.id) + " AND channel_id=" +str(channel_id))
                    print("Done")
                else:
                    print("?")
        except Exception as error:
            print(error)
    else:
        print("Not a list")