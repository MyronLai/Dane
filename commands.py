import asyncio

async def displayHelpDirectory(client, channel):
    await client.send_message(channel, "You triggered the help command.")

async def assignRole(client, member, role):
    # Needs to add a role to the user.
    await client.add_roles(member, role)
    print("Adding role..")
