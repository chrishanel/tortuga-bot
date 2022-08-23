import fandom
import random

fandom.set_wiki("effectivelywild")


"""
Use the Fandom API to search for episode by number
"""


def search_for_episode_by_number(episode_number):
    search_results = fandom.search(episode_number)
    for result in search_results:
        page_name = result[0]
        result_episode_number = page_name.split(":")[0].split("Episode ")[1]
        if int(result_episode_number) == int(episode_number):
            episode_page = fandom.page(page_name)
            return episode_page
    return None


"""
Use the Fandom API to retrieve a random episode
"""


def search_for_random_episode():
    search_results = fandom.search("episode")
    episode = random.choice(search_results)[0]
    episode_page = fandom.page(episode)
    return episode_page


def encode_episode_url(url):
    return url.replace("?", "%3f")
