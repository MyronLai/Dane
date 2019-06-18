async def subscribe_user(user_id, ctx, database):
    # Need to query database and check if User Exists in the VoiceChannelSubscriptions Table
    cursor = database.cursor()
    cursor.execute("SELECT * FROM VoiceChannelSubscriptions WHERE client_id=" + str(user_id) + " AND channel_id=" + str(ctx.channel.id))
    results = cursor.fetchall()
    print(results)
    if len(results) == 0: # Insert the  user into the database, set isSubscribed to 1.
        cursor.execute("INSERT INTO VoiceChannelSubscriptions VALUES(" + str(ctx.channel.id) + "," + str(ctx.guild.id) + "," + str(user_id) + ", 1)")
        print("Done")
    else:
        cursor.execute("UPDATE VoiceChannelSubscriptions SET isSubscribed=1 WHERE client_id=" + str(user_id) + " AND channel_id=" + str(ctx.channel.id))
        print("Done")