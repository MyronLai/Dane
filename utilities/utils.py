import asyncio
import discord.abc
import re
from utilities.cache import Cache
from database.keywords import SQLKeywords
from utilities.courses import *

cache = Cache()
cache.start()

PRIORITY_CHANNELS = ['welcome', 'member-log', 'mod-logs', 'mod-channel', 'rules-and-info']

def hasRole(member, role):
    memberRoles = member.roles
    currentRole = discord.utils.find(lambda r : r.name.lower() == role.lower(), memberRoles)
    print(currentRole)
    return currentRole != None

def parse_help_msg(msg):
    return re.sub('(```[\n\t]*)', '', msg)


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

async def remove_roles(ctx, roles):
    roles = re.sub(',\s+', ',', roles) # Replace all occurences of a comma and any number of whitespace with just a comma.
    roles = roles.split(",")
    print(roles)
    roles_list = []
    for role_name in roles:
        role = discord.utils.find(lambda r : r.name.lower() == role_name.lower(), ctx.guild.roles)
        roles_list.append(role) if role is not None else None

    await ctx.author.remove_roles(*roles_list)

async def add_roles(ctx, roles):
    roles = re.sub(',\s+', ',', roles) # Replace all occurences of a comma and any number of whitespace with just a comma.
    roles = roles.split(",")
    valid_roles = []
    for role in roles:
        valid_role = discord.utils.find(lambda r: r.name.lower() == role.lower(), ctx.guild.roles)
        if valid_role is not None:
            perms = valid_role.permissions
            if perms.kick_members or perms.ban_members or perms.administrator or perms.manage_channels or perms.manage_guild or perms.manage_messages:
                print("Cannot add user to " + valid_role.name)
                pass
            else:
                valid_roles.append(valid_role)
    
    await ctx.author.add_roles(*valid_roles) # Unpack the list and pass it to add_roles.

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
            course_results = await getCourses(args[1], args[2])
            await build_embeds(message, course_results, args, cache_key)
            
    elif len(args) == 4: # If 4, they specified a professor.
        cache_key = args[1]+args[2]+args[3]
        if cache_key in cache.get_cache():
            print("Exists. Get data from Cache.")
            cached_embeds = cache.get(cache_key)
            for embeds in cached_embeds:
                await message.channel.send(embed=embeds)

        else:
            course_results = await getCourses(args[1], args[2])
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

async def kickUser(ctx, user_id, reason):
    user = discord.utils.find(lambda u: u.id==int(user_id), ctx.guild.members)
    if ctx.channel.permissions_for(ctx.author).kick_members and user is not None: # Check if they have kick_members permissions
        if ctx.channel.permissions_for(ctx.author).value > ctx.channel.permissions_for(user).value:
            await user.kick(reason=reason)
        else:
            print('No permissions.')
    else:
        print("non admin/mod trying to use kick command")
def isAdmin(ctx, user_id):
    # Find User 
    user = discord.utils.get(ctx.guild.members, id=int(user_id))
    if user is not None:
        return ctx.message.channel.permissions_for(user).administrator
    else:
        return False
