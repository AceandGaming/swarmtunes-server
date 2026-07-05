import logging

import requests

log = logging.getLogger()

emotes = {}


def load_emotes():
    global emotes
    twitchEmotes = []

    swarmFMResponse = requests.get(
        "https://7tv.io/v3/emote-sets/01K1H87ZZVE92Y3Z37H3ES6BK8"
    )  # swarmfm
    if swarmFMResponse.status_code == 200:
        twitchEmotes.extend(swarmFMResponse.json()["emotes"])
    else:
        log.error("Failed to get swarmfm emotes")

    vedalResponse = requests.get(
        "https://7tv.io/v3/emote-sets/01GN2QZDS0000BKRM8E4JJD3NV"
    )  # vedal987
    if vedalResponse.status_code != 200:
        log.exception("Failed to get vedal987 emotes")
        return
    twitchEmotes.extend(vedalResponse.json()["emotes"])

    for emote in twitchEmotes:
        url = "https:" + emote["data"]["host"]["url"]
        emotes[emote["name"]] = url


def get_emote(name):
    return emotes.get(name)
