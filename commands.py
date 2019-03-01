import asyncio
import discord

def hasRole(member, role):
    memberRoles = member.roles
    currentRole = discord.utils.find(lambda r : r.name.lower() == role.lower(), memberRoles)
    print(memberRoles)

    if memberRoles == None:
        return false
    else:
        return true

async def displayHelpDirectory(client, channel):
    await client.send_message(channel, "You triggered the help command.")

async def assignRole(client, message):
    # Needs to add a role to the user.
    roles = message.server.roles
    args = message.content.split()
    ROLE_TO_ASSIGN = discord.utils.find(lambda r: r.name.lower() == args[1].lower(), roles)

    # Need to check if the user has the role, if they do, we shouldn't need to add them.

    if ROLE_TO_ASSIGN == None:
        embed = discord.Embed()
        embed.title = 'Error'
        embed.description = 'Role not found.'
        embed.color = 16711680
        await client.send_message(message.channel, embed = embed)
        return

    if hasRole(message.author, args[1]):
        print("User has role")
        return

    else:
        await client.add_roles(message.author, ROLE_TO_ASSIGN)
        embed = discord.Embed()
        embed.title = 'Success'
        embed.description = 'Added to role'
        embed.color = 65280
        await client.send_message(message.channel, embed = embed)

async def removeRole(client, message):
    print("Removing a role")
