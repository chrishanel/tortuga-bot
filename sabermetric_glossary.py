import json
import discord

with open('messages.json', 'r') as message_file:
    message_data = json.load(message_file)
    glossary = message_data['sabermetric_glossary']

async def send_metric(client, metric):
    embed=discord.Embed(title=f"Sabermetric Glossary: {metric['name']}")
    embed.add_field(name="Definition", value=metric['definition'], inline=False)
    record = metric['record']
    embed.add_field(name=f"Record {metric['name']}", value=f"{record['value']} - {record['holder']}, {record['year']}", inline=True)
    await client.send(embed=embed)

async def send_metric_by_name(client, metric_name):
    await send_metric(client, glossary[metric_name])

async def try_send_message(client, message):
    target_metric = message.content.lower().split("!stat")[1].strip()
    if target_metric not in glossary:
        print(f"Error: couldn't find stat called {target_metric}")
        return
    
    await send_metric_by_name(client, target_metric)
    
