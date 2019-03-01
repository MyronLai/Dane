import asyncio
import discord

async def displayHelpDirectory(client, channel):
    await client.send_message(channel, "You triggered the help command.")

async def assignRole(client, message):
    # Needs to add a role to the user.
    roles = message.server.roles
    args = message.content.split()
    ROLE_TO_ASSIGN = discord.utils.find(lambda r: r.name.lower() == args[1].lower(), roles)

    if ROLE_TO_ASSIGN == None:
        print("Role not found")

    else:
        await client.add_roles(message.author, ROLE_TO_ASSIGN)
        print("Adding role..")
