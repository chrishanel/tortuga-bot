import traceback
import discord
import json
from wiki_functions import *

al_role_dict = {"Orioles": "<:BAL:907714486507565096>", "Red Sox": "<:BOS:907714486604013678>", "Guardians": "<:CLE:907714486583033957>",
                "White Sox": "<:CWS:907714486591434822>", "Tigers": "<:DET:907714487476445235>", "Astros": "<:HOU:907714485467357186>",
                "Royals": "<:KCR:907714486243299328>", "Angels": "<:LAA:907714485425430528>", "Twins": "<:MIN:907714486297829397>",
                "Yankees": "<:NYY:907714485895200779>", "Athletics": "<:OAK:907714486029389854>", "Mariners": "<:SEA:907714486448816128>",
                "Rays": "<:TBR:907714486121664576>", "Rangers": "<:TEX:907714486062948412>", "Blue Jays": "<:TOR:907714486281072690>"}
nl_role_dict = {"Diamondbacks": "<:ARI:907714486473986078>", "Braves": "<:ATL:907714485702246420>", "Cubs": "<:CHC:907714487472250880>",
                "Reds": "<:CIN:907714487468048385>", "Rockies": "<:COL:907714485857427517>", "Dodgers": "<:LAD:907714485756772402>",
                "Marlins": "<:MIA:907714487606464572>", "Brewers": "<:MIL:907714487610671104>", "Mets": "<:NYM:907714485941329960>",
                "Phillies": "<:PHI:907714486037778502>", "Pirates": "<:PIT:907714486033608714>", "Padres": "<:SDP:907714487602274324>",
                "Giants": "<:SFG:907714485807112262>", "Cardinals": "<:STL:907714487266738268>", "Nationals": "<:WAS:907714485844852747>"}

with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)

with open('messages.json', 'r') as message_file:
    message_data = json.load(message_file)

# Handle if testing or not
if config_data['test_mode'] == "ON":
    welcome_channel_id = config_data['test_channel_id']
else:
    welcome_channel_id = config_data['welcome_channel_id']

bot_id = config_data['bot_id']
welcome_message = message_data['welcome_message']
al_message = message_data['al_message']
nl_message = message_data['nl_message']

"""
Check the welcome channel and verify the message to react to in order to assign roles has not been posted
"""


async def verify_message_posted(channel, message):
    messages = await channel.history(limit=50).flatten()
    for msg in messages:
        if message in msg.content:
            print("Message found. Do not post.")
            return True
    print("Message not found. Posting...")
    return False


"""
Check if the message to react to has been created, if not, create it. If so, ignore.
"""


async def create_react_message(client):
    try:
        channel = client.get_channel(int(welcome_channel_id))
        if not await verify_message_posted(channel, welcome_message):
            await channel.send(welcome_message)
        if not await verify_message_posted(channel, "American League"):
            message_sent = await channel.send(al_message)
            message_data['al_message_id'] = message_sent.id     # Update the json file with the message's ID
            await add_reaction(message_sent, al_role_dict)
        if not await verify_message_posted(channel, "National League"):
            message_sent = await channel.send(nl_message)
            message_data['nl_message_id'] = message_sent.id     # Update the json file with the message's ID
            await add_reaction(message_sent, nl_role_dict)
    except discord.Forbidden:
        print("WARNING: I do not have permission to post messages, please give #welcome permissions and restart me.")


"""
Add team emojis to each message
"""


async def add_reaction(message, role_dict):
    for team_emoji in role_dict.values():
        await message.add_reaction(team_emoji)


async def find_if_assigned_max_roles(user):
    user_roles = user.roles
    role_count = 0
    for role in user_roles:
        # If the user has hit the max number of teams, return true
        if role_count >= 3:
            return True
        if role.name in al_role_dict.keys() or role.name in nl_role_dict.keys():
            role_count = role_count + 1
    return False


"""
Set the user's role based on what team they react to the message with
"""


async def request_add_role(client, payload):
    channel = client.get_channel(int(welcome_channel_id))
    message = await channel.fetch_message(payload.message_id)
    guild = await client.fetch_guild(payload.guild_id)
    user = payload.member

    # Verify the bot isn't requesting to add a role for itself
    if payload.user_id == int(bot_id):
        return

    al_message_react = await channel.fetch_message(int(message_data['al_message_id']))
    nl_message_react = await channel.fetch_message(int(message_data['nl_message_id']))
    # Check if the new team the user attempted to add was AL and remove reaction if hit max
    if await find_if_assigned_max_roles(user):
        if str(payload.emoji) in al_role_dict.values():
            await al_message_react.remove_reaction(payload.emoji, user)
            print("User already has max number of roles! Did not add second role.")
            return
        elif str(payload.emoji) in nl_role_dict.values():
            await nl_message_react.remove_reaction(payload.emoji, user)
            print("User already has max number of roles! Did not add second role.")
            return
        else:
            print("User already has max number of roles! Could not remove reaction")
            return

    # Verify the message is in the welcome channel, as it should be
    if message.channel.id != int(welcome_channel_id):
        print("WARNING: The message's channel ID does not match the welcome channel ID")
        return

    # AL role requested, go through AL teams
    if "American League" in message.content:
        await set_role(payload, user, guild, al_role_dict)
    # NL role requested, go through NL teams
    elif "National League" in message.content:
        await set_role(payload, user, guild, nl_role_dict)


"""
At the request of a user, remove them from a team role
"""


async def request_delete_role(client, message):
    user = message.author
    guild = message.guild
    team = message.content.lower().split("!remove")[1].strip()
    nl_message_id = int(message_data['nl_message_id'])
    al_message_id = int(message_data['al_message_id'])
    welcome_channel = client.get_channel(int(welcome_channel_id))

    remove_message = discord.Embed(color=0x50AE26)

    for team_role, team_emoji in al_role_dict.items():
        if team.lower() == team_role.lower():
            try:
                role = discord.utils.get(guild.roles, name=team_role)
                await user.remove_roles(role)
                reaction_message = await welcome_channel.fetch_message(al_message_id)
                await reaction_message.remove_reaction(team_emoji, user)
                print("Removed " + user.name + " from " + team_role)
                remove_message.add_field(name="SUCCESS", value="Successfully removed the " + team_role + " role", inline=False)
                await message.channel.send(embed=remove_message)
                return
            except:
                print("Error removing " + user.name + " from " + team_role + ". Please see stack trace below for more info")
                traceback.print_exc()

    for team_role, team_emoji in nl_role_dict.items():
        if team.lower() == team_role.lower():
            try:
                role = discord.utils.get(guild.roles, name=team_role)
                await user.remove_roles(role)
                reaction_message = await welcome_channel.fetch_message(nl_message_id)
                await reaction_message.remove_reaction(team_emoji, user)
                print("Removed " + user.name + " from " + team_role)
                remove_message.add_field(name="SUCCESS", value="Successfully removed the " + team_role + " role", inline=False)
                await message.channel.send(embed=remove_message)
                return
            except:
                print("Error removing " + user.name + " from " + team + ". Please see stack trace below for more info")
                traceback.print_exc()

    remove_message.add_field(name="ERROR", value="Failed to remove the " + team + " role, please verify the role name is correct and the role is assigned to you.", inline=False)
    await message.channel.send(embed=remove_message)
    print("Error removing the " + team + " role from " + user.name)


"""
Iterate through the specified league's teams and set the role for the user to the specified team
"""


async def set_role(payload, user, guild, role_dict):
    for team_role, team_emoji in role_dict.items():
        if str(payload.emoji) == team_emoji:
            try:
                role = discord.utils.get(guild.roles, name=team_role)
                await user.add_roles(role)
                print("Added " + user.name + " to " + team_role)
            except:
                print("Error adding " + user.name + " to " + team_role + ". Please see stack trace below for more info")
                traceback.print_exc()


"""
Search through the wiki and find the requested episode and respond with a link to it
"""
async def request_episode(message):
    # content is known to begin with !ep or !episode
    # strip off the prefix
    content = message.content.lower()
    rest = content[3:]
    if (rest.startswith("isode")):
        rest = rest[5:]

    search_episode = rest.split()[0]

    episode_message = discord.Embed(color=0x50AE26)

    # If user wants to be given a random episode
    if not str.isdigit(search_episode) and (search_episode == "random" or search_episode == "r"):
        episode_page = search_for_random_episode()
        if episode_page is None:
            episode_message.add_field(name="ERROR", value="Could not find an episode.", inline=False)
            print("Error: Could not find a random episode")
        else:
            episode_message.add_field(name=episode_page.title, value=encode_episode_url(episode_page.url), inline=False)
            print("Found " + episode_page.title + "!")

    # If user wants a specific episode
    elif str.isdigit(search_episode):
        episode_page = search_for_episode_by_number(search_episode)
        if episode_page is None:
            episode_message.add_field(name="ERROR", value="Could not find episode " + search_episode, inline=False)
            print("Error: Could not find Episode " + search_episode + ".")
        else:
            episode_message.add_field(name=episode_page.title, value=encode_episode_url(episode_page.url), inline=False)
            print("Found Episode " + search_episode + "!")

    # If could not query
    else:
        episode_message.add_field(name="ERROR", value="Could not search for episode, please send a request with an episode number", inline=False)

    await message.channel.send(embed=episode_message)
