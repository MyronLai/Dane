import asyncio
import discord
import courses
import re

PRIORITY_CHANNELS = ['welcome', 'member-log', 'mod-logs', 'mod-channel', 'rules-and-info']
def hasRole(member, role):
    memberRoles = member.roles
    currentRole = discord.utils.find(lambda r : r.name.lower() == role.lower(), memberRoles)
    print(currentRole)
    return currentRole != None

async def display_help(ctx, database):
    cursor = database.cursor()
    print("Hello.?")
    cursor.execute("SELECT help_msg FROM Guilds WHERE guild_id = " +  str(ctx.guild.id))
    result = cursor.fetchall()
    msg = result[0][0]
    embed = discord.Embed()
    embed.title = 'Server Message'
    embed.description = msg
    embed.color = 13951737

    await ctx.channel.send(embed=embed)

async def assignRole(client, message):
    # Needs to add a role to the user.
    roles = message.guild.roles
    args = re.sub("^(\?assign( )*)", "", message.content)
    args = re.split(" *, *", args)
    print(args)
    if len(args) == 1 and len(args[0]) == 0:
        embed = discord.Embed()
        embed.title = 'Too few arguments'
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        embed.description = "?assign <role1, role2, ...>"
        embed.color = 4366836
        await message.channel.send(embed=embed)
        return
    # Need to check array length, for each role in the array, we will loop and check if the role exists.

    counter = 0 # Counter to start at zero.

    rolesSuccess = []
    rolesFailure = []

    for currRole in args:
        ROLE_TO_ASSIGN = discord.utils.find(lambda r: r.name.lower() == args[counter].lower(), roles)
        # Need to check if the user has the role, if they do, we shouldn't need to add them.

        if ROLE_TO_ASSIGN == None:
            embed = discord.Embed()
            embed.title = 'Error'
            embed.description = 'Role not found.'
            embed.color = 16711680
            rolesFailure.append(args[counter])
            await message.channel.send(embed = embed)

        if hasRole(message.author, args[counter]):
            embed = discord.Embed()
            embed.title = 'Error'
            embed.description = 'User already assigned to role.'
            embed.color = 16711680
            rolesFailure.append(args[counter])
            await message.channel.send(embed = embed)

        else:
            await message.author.add_roles(ROLE_TO_ASSIGN)
            embed = discord.Embed()
            embed.title = 'Success'
            embed.description = 'Added to role'
            embed.color = 65280
            rolesSuccess.append(args[counter])
            await message.channel.send(embed = embed)

        counter += 1

    # End of For Loop.

async def removeRole(client, message):
    roles = message.guild.roles
    args = message.content.split()
    args.pop(0)
    counter = 0

    for currRole in args:
        ROLE_TO_REMOVE = discord.utils.find(lambda r : r.name.lower() == args[counter].lower(), roles)

        if hasRole(message.author, args[counter]):
            await message.author.remove_roles(ROLE_TO_REMOVE)
            print("Removed.")

        counter += 1

async def queryCourse(client, message):

    args = message.content.split(" ")
    course_results = await courses.getCourses(args[1], args[2])

    currentEmbed = discord.Embed()
    if len(course_results['courses']) != 0:
        arrayOfEmbeds = []

        i = 0
        for currentCourse in course_results['courses']:
            if i < 25: # New Embed with max 25 fields.
                if i != 20: # Only append blank fields if the result isn't the last result.
                    currentEmbed.add_field(name="Class Number", value=currentCourse['class'])
                    currentEmbed.add_field(name="Class Info", value=currentCourse['courseInfo'])
                    currentEmbed.add_field(name="Meeting", value=currentCourse['meeting'])
                    currentEmbed.add_field(name="Seats Left", value=currentCourse['seatsLeft'], inline=False)
                    currentEmbed.add_field(name="\u200b", value="\u200b",inline=False)
                    currentEmbed.color = 4382708
                else:
                    currentEmbed.add_field(name="Class Number", value=currentCourse['class'])
                    currentEmbed.add_field(name="Class Info", value=currentCourse['courseInfo'])
                    currentEmbed.add_field(name="Meeting", value=currentCourse['meeting'])
                    currentEmbed.add_field(name="Seats Left", value=currentCourse['seatsLeft'], inline=False)
                    currentEmbed.set_footer(text="Fall 2019 Semester") # Set footer because this is the last result of embed.
                    currentEmbed.color = 4382708
                i += 5
            else:
                await message.channel.send(embed=currentEmbed)
                arrayOfEmbeds.append(currentEmbed)
                currentEmbed.clear_fields()
                i = 0
        
        if len(arrayOfEmbeds) == 0:
            currentEmbed.set_footer(text="Fall 2019 Semester")
            arrayOfEmbeds.append(currentEmbed)
        
        for embed in arrayOfEmbeds:
            await message.channel.send(embed=embed)
    else:
        currentEmbed.title='Error. Course not found'
        currentEmbed.description=args[1].upper() + ' ' + args[2] + ' was not found. Please try another search'
        currentEmbed.color=9633965
        await message.channel.send(embed=currentEmbed)
    

# THIS IS AN ADMIN FUNCTION 
async def pruneMessages(message, user_id):
    # Check if the user who issued the command has permission.
    isAdmin = message.author.permissions_in(message.channel).administrator
    owner = message.guild.owner
    channel = message.channel

    if channel.name in PRIORITY_CHANNELS:
        print("Cannot purge messages in a priority channel.")
        return
    # If the user is an Admin, then we can proceed to prune the messages.
    if isAdmin:
        print('User is an admin. Deleting...')
        # Check if the messages to be deleted were sent by an Admin.
        user = discord.utils.find(lambda u : u.id == user_id, message.guild.members) # Get the author of the messages to purge
        if user is not None: 
            guild_perms = message.channel.permissions_for(user).administrator

            if owner.id == user_id or user_id == message.author.id:
                print("Owner is deleting another admin's messages.")
                await channel.purge(limit=50, check=(lambda m : int(m.author.id) == user_id))
            
            elif guild_perms: # If messages were by another Admin. Don't delete. We will make it so the owner can delete any Admin's messages.
                print('You cannot delete messages of another Admin')
            else:
                print("Deleting..")
                await channel.purge(limit=50, check=(lambda m : int(m.author.id) == user_id))


    else:
        print('User is not an admin, not deleting.')
        
'''
Admins cannot ban other admins
'''
async def assignUserBan(context, user_id, reason):
    message = context.message
    isAdmin = message.channel.permissions_for(message.author).administrator

    channel = context.channel

    userToBan = discord.utils.get(context.guild.members, id=int(user_id))
    if userToBan is not None:
        # Check if user is an Administrator
        print(userToBan.name)
        isUserToBanAnAdmin = channel.permissions_for(userToBan).administrator
        print(isUserToBanAnAdmin)
        if isUserToBanAnAdmin:
            print("Cannot ban another admin.")
        else:
            await context.guild.ban(userToBan, delete_message_days=1, reason=reason)

async def kickUser(ctx, user_id, reason):
    admin = isAdmin(ctx, ctx.message.author.id)
    
    isUserToKickAnAdmin = isAdmin(ctx, user_id)
    userToKick = discord.utils.get(ctx.guild.members, id=user_id)
    if isUserToKickAnAdmin:
        print('Cannot kick another admin with this command')
    elif admin:
        await ctx.guild.kick(userToKick, reason=reason)

def isAdmin(ctx, user_id):
    # Find User 
    user = discord.utils.get(ctx.guild.members, id=int(user_id))
    if user is not None:
        return ctx.message.channel.permissions_for(user).administrator
    else:
        return False