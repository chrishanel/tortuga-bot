import json
import discord

with open('messages.json', 'r') as message_file:
    message_data = json.load(message_file)
    glossary = message_data['sabermetric_glossary']


"""
Send the metric back to Discord

"""


async def send_metric(message, metric):
    embed = discord.Embed(title=f"Sabermetric Glossary: {metric['name']}")
    embed.add_field(name="Definition", value=metric['definition'], inline=False)
    record = metric['record']
    embed.add_field(name=f"Record {metric['name']}", value=f"{record['value']} - {record['holder']}, {record['year']}",
                    inline=True)
    await message.channel.send(embed=embed)


"""
Send the metric via name

"""


async def send_metric_by_name(message, metric_name):
    await send_metric(message, glossary[metric_name])

"""
List available metrics
"""


async def send_list_message(message):
    embed = discord.Embed(title=f"Sabermetric Glossary")
    available_metrics = "\n".join([f"!stat {glossary[k]['name']}" for k in list(glossary.keys())])
    embed.add_field(name="Available Metrics", value=available_metrics, inline=False)
    await message.channel.send(embed=embed)

"""
Try to send the metric back to Discord, give an error if it could not find the stat

"""


async def try_send_metric(client, message):
    target_metric = message.content.lower().split("!stat")[1].strip()
    if target_metric == "list":
        await send_list_message(message)
        return
    if target_metric not in glossary:
        print(f"Error: couldn't find stat called {target_metric}")
        error_message = discord.Embed(color=0x50AE26)
        error_message.add_field(name="ERROR",
                                value="Couldn't find a stat called " + target_metric + "\nTry !stat list for a list of available metrics",
                                inline=False)
        await message.channel.send(embed=error_message)
        return

    await send_metric_by_name(message, target_metric)
