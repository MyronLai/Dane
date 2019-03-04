import asyncio
import discord
import courses
import re

def hasRole(member, role):
    memberRoles = member.roles
    currentRole = discord.utils.find(lambda r : r.name.lower() == role.lower(), memberRoles)
    print(currentRole)
    return currentRole != None

async def displayHelpDirectory(client, channel):
    await client.send_message(channel, "You triggered the help command.")

async def assignRole(client, message):
    # Needs to add a role to the user.
    roles = message.server.roles
    args = re.sub("^(\?assign( )*)", "", message.content)
    args = re.split(" *, *", args)
    print(args)
    if len(args) == 1 and len(args[0]) == 0:
        embed = discord.Embed()
        embed.title = 'Too few arguments'
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        embed.description = "?assign <role1, role2, ...>"
        embed.color = 4366836
        await client.send_message(message.channel, embed=embed)
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
            await client.send_message(message.channel, embed = embed)

        if hasRole(message.author, args[counter]):
            embed = discord.Embed()
            embed.title = 'Error'
            embed.description = 'User already assigned to role.'
            embed.color = 16711680
            rolesFailure.append(args[counter])
            await client.send_message(message.channel, embed = embed)

        else:
            await client.add_roles(message.author, ROLE_TO_ASSIGN)
            embed = discord.Embed()
            embed.title = 'Success'
            embed.description = 'Added to role'
            embed.color = 65280
            rolesSuccess.append(args[counter])
            await client.send_message(message.channel, embed = embed)

        counter += 1

    # End of For Loop.

async def removeRole(client, message):
    roles = message.server.roles
    args = message.content.split()
    args.pop(0)
    counter = 0

    for currRole in args:
        ROLE_TO_REMOVE = discord.utils.find(lambda r : r.name.lower() == args[counter].lower(), roles)

        if hasRole(message.author, args[counter]):
            await client.remove_roles(message.author, ROLE_TO_REMOVE)
            print("Removed.")

        counter += 1

async def queryCourse(client, message):

    args = message.content.split(" ")
    print(args)
    course_results = await courses.getCourses(args[1], args[2])
    for currentCourse in course_results['courses']:
        embed = discord.Embed()
        embed.color = 4382708
        embed.add_field(name="Class Number", value=currentCourse['class'])
        embed.add_field(name="Class Info", value=currentCourse['courseInfo'])
        embed.add_field(name="Meeting", value=currentCourse['meeting'])
        embed.add_field(name="Seats Left", value=currentCourse['seatsLeft'], inline=False)
        embed.set_footer(text="Fall 2019 Semester")
        await client.send_message(message.channel, embed=embed)
