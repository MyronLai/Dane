import asyncio
import discord
import courses
import re
from cache import Cache
from database.keywords import SQLKeywords

cache = Cache()
cache.start()

PRIORITY_CHANNELS = ['welcome', 'member-log', 'mod-logs', 'mod-channel', 'rules-and-info']

def hasRole(member, role):
    memberRoles = member.roles
    currentRole = discord.utils.find(lambda r : r.name.lower() == role.lower(), memberRoles)
    print(currentRole)
    return currentRole != None

async def display_help(ctx, database):
    cursor = database.cursor()
    cursor.execute("SELECT help_msg FROM Guilds WHERE guild_id = " +  str(ctx.guild.id))
    result = cursor.fetchall()
    msg = result[0][0]
    embed = discord.Embed()
    embed.title = 'Help Directory & Information'
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

async def build_embeds(message, course_results, args, cache_key):
    if len(course_results['courses']) != 0:
        arrayOfEmbeds = []
        i = 0
        currentEmbed = discord.Embed()
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
                print('no add here')
                arrayOfEmbeds.append(currentEmbed.copy()) # Add a copy of the embed
                currentEmbed = discord.Embed() # Reset the embed to a new objeect.
                i = 0
        
        if len(arrayOfEmbeds) == 0: # If the length of the array is 0, that means an embed of less than 25 fields was built.
            print('yes french')
            currentEmbed.set_footer(text="Fall 2019 Semester")
            arrayOfEmbeds.append(currentEmbed.copy())

        else: # The last embed was not added, so add it to the array.
            if len(currentEmbed.fields) == 0:
                pass
            else:
                arrayOfEmbeds.append(currentEmbed.copy())
            
        for embed in arrayOfEmbeds: # Iterate through all embeds and send them.
            await message.channel.send(embed=embed)

        cache.add(cache_key, arrayOfEmbeds)

    else:
        currentEmbed=discord.Embed()
        currentEmbed.title='Error. Course not found'
        currentEmbed.description=args[1].upper() + ' ' + args[2] + ' was not found. Please try another search'
        currentEmbed.color=9633965
        await message.channel.send(embed=currentEmbed)

async def build_embeds_prof(course_results, message, args, search_term, cache_key):

    if len(course_results['courses']) != 0:
        arrayOfEmbeds = []
        i = 0
        currentEmbed = discord.Embed()
        for currentCourse in course_results['courses']:
            meeting = currentCourse['meeting'].strip()
            result = re.search(search_term.lower(), meeting.lower())
            if result is not None:
                print("Found for " + meeting)
                if i < 25:
                    if i != 20:
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
                    i+=5
                else:
                    arrayOfEmbeds.append(currentEmbed.copy()) # Add a copy of the embed
                    currentEmbed = discord.Embed() # Reset the embed to a new objeect.
                    i = 0
                
        if len(arrayOfEmbeds) == 0: # If the length of the array is 0, that means an embed of less than 25 fields was built.
            if len(currentEmbed.fields) == 0:
                # No professors were found.
                currentEmbed.title='Error. Course not found'
                currentEmbed.description='No course was found for ' + args[1] + ' ' + args[2] + ' ' + args[3]
                currentEmbed.color=9633965
                arrayOfEmbeds.append(currentEmbed.copy())
            else:
                currentEmbed.set_footer(text="Fall 2019 Semester")
                print('yes, empty')
                arrayOfEmbeds.append(currentEmbed.copy()) # Add a copy.

        else: # The last embed was not added, so add it to the array.
            currentEmbed.set_footer(text="Fall 2019 Semester")
            arrayOfEmbeds.append(currentEmbed.copy())
            
        for embed in arrayOfEmbeds: # Iterate through all embeds and send them.
            await message.channel.send(embed=embed)

        cache.add(cache_key, arrayOfEmbeds)
    else:
        currentEmbed=discord.Embed()
        currentEmbed.title='Error. Course not found'
        currentEmbed.description=args[1].upper() + ' ' + args[2] + ' '  + args[3] + ' was not found. Please try another search'
        currentEmbed.color=9633965
        await message.channel.send(embed=currentEmbed)

async def queryCourse(client, message):

    args = message.content.split(" ")

    if len(args) == 3:
        cache_key = args[1]+args[2]
        if cache_key in cache.get_cache():
            print("Exists. Get data from Cache.")
            cached_embeds = cache.get(cache_key)
            for embeds in cached_embeds:
                await message.channel.send(embed=embeds)
        else:
            print("Does not exist in cache.")
            course_results = await courses.getCourses(args[1], args[2])
            await build_embeds(message, course_results, args, cache_key)
            
    elif len(args) == 4: # If 4, they specified a professor.
        cache_key = args[1]+args[2]+args[3]
        if cache_key in cache.get_cache():
            print("Exists. Get data from Cache.")
            cached_embeds = cache.get(cache_key)
            for embeds in cached_embeds:
                await message.channel.send(embed=embeds)

        else:
            course_results = await courses.getCourses(args[1], args[2])
            currentEmbed = discord.Embed()
            search_term = args[3]
            print(search_term)
            await build_embeds_prof(course_results, message,args, search_term, cache_key)
        
        
    else:
        embed=discord.Embed()
        embed.title='API Error'
        embed.description='Too many arguments. Usage: ?course <subject> <code> <professor?>'
        embed.color=9633965
        await message.channel.send(embed=embed)

'''
    Prunes a given number of messages in a channel. This is an Admin function and should be used carefully.

    args:
        message (Message): The message object
        user_id (int): The id of the user's messages to delete
        prune_all (boolean) : Whether to prune all messages or only by user id.
    
    returns:
        boolean: True if successful, False otherwise.
'''
async def prune_messages(message, user_id=-1, prune_all=True):
    # Check if the user who issued the command has permission.
    print("Hello")
    print(user_id)
    '''isAdmin = message.author.permissions_in(message.channel).administrator
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
                await channel.purge(limit=50, check=(lambda m : int(m.author.id) == user_id))'''
    def is_owner(): # Return true if the person using the command is owner.
        return message.author.id == message.guild.owner_id

    if prune_all: # Prune all messages should only be available to owner.
        print("Pruning ALL messages, regardless of who the author is.")
        if is_owner():
            await message.channel.purge(limit=50)
            # Should add a check to prevent Admins from deleting Owner Messages.

    else:
        print("Pruning " + str(user_id))
        owner_id = message.guild.owner_id
        if message.author.id == owner_id:
            await message.channel.purge(limit=50, check=(lambda m: int(m.author.id == user_id)))

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
'''
def get_sql_statement(key, *args):

    if key == SQLKeywords.SELECT:
        columns=args[0]
        table=args[1]
        values=args[2]
        col_str =  ' '.join(columns)
        return SQLKeywords.SELECT.value + ' ' + col_str + ' FROM ' + table.value
    elif key == SQLKeywords.INSERT:
        
        pass
    elif key == SQLKeywords.CREATE:
        pass
    elif key == SQLKeywords.DELETE:
        pass
    elif key == SQLKeywords.ALTER_COLUMN:
        pass
    elif key == SQLKeywords.ALTER_TABLE:
        pass
        '''