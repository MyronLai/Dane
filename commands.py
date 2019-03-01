import asyncio
import discord

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
    args = message.content.split()

    # Need to check array length, for each role in the array, we will loop and check if the role exists.
    
    args.pop(0)
    counter = 0 # Counter to start at zero.
    for currRole in args:
        print(currRole)
        ROLE_TO_ASSIGN = discord.utils.find(lambda r: r.name.lower() == args[counter].lower(), roles)
        # Need to check if the user has the role, if they do, we shouldn't need to add them.

        if ROLE_TO_ASSIGN == None:
            embed = discord.Embed()
            embed.title = 'Error'
            embed.description = 'Role not found.'
            embed.color = 16711680
            await client.send_message(message.channel, embed = embed)
            return

        if hasRole(message.author, args[counter]):
            embed = discord.Embed()
            embed.title = 'Error'
            embed.description = 'User already assigned to role.'
            embed.color = 16711680
            await client.send_message(message.channel, embed = embed)
            return

        else:
            await client.add_roles(message.author, ROLE_TO_ASSIGN)
            embed = discord.Embed()
            embed.title = 'Success'
            embed.description = 'Added to role'
            embed.color = 65280
            await client.send_message(message.channel, embed = embed)

        counter += 1


async def removeRole(client, message):
    print("Removing a role")
