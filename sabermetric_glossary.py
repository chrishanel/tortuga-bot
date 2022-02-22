import json
import discord

with open('messages.json', 'r') as message_file:
    message_data = json.load(message_file)
    glossary = message_data['sabermetric_glossary']


"""
Send the metric back to Discord

"""


async def send_metric(client, metric):
    embed = discord.Embed(title=f"Sabermetric Glossary: {metric['name']}")
    embed.add_field(name="Definition", value=metric['definition'], inline=False)
    record = metric['record']
    embed.add_field(name=f"Record {metric['name']}", value=f"{record['value']} - {record['holder']}, {record['year']}",
                    inline=True)
    await client.send(embed=embed)


"""
Send the metric via name

"""


async def send_metric_by_name(client, metric_name):
    await send_metric(client, glossary[metric_name])


"""
Try to send the metric back to Discord, give an error if it could not find the stat

"""


async def try_send_metric(client, message):
    target_metric = message.content.lower().split("!stat")[1].strip()
    if target_metric not in glossary:
        print(f"Error: couldn't find stat called {target_metric}")
        error_message = discord.Embed(color=0x50AE26)
        error_message.add_field(name="ERROR",
                                 value="Couldn't find a stat called " + target_metric,
                                 inline=False)
        await message.channel.send(embed=error_message)
        return

    await send_metric_by_name(client, target_metric)
