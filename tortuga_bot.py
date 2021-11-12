"""
Tortuga Bot for the Effectively Wild Discord

@author: Andrew Kicklighter
"""

import discord
import json

from discord_functions import *

"""
Call the commands and run the bot
"""


def run_tortuga_bot():
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
    token = config_data['discord_token']

    client = discord.Client()

    @client.event
    async def on_raw_reaction_add(payload):
        await request_add_role(client, payload)

    @client.event
    async def on_message(message):
        if message.content.lower().startswith("!remove"):
            await request_delete_role(client, message)

        if message.content.lower().startswith("!stat"):
            await send_saber_response(client, message)

    @client.event
    async def on_ready():
        print('------')
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

        await create_react_message(client)

    client.run(token)


# Main method
if __name__ == '__main__':
    run_tortuga_bot()
