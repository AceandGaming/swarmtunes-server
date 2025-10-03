import requests

emotes = {}
def Load():
    global emotes
    twitchEmotes = []

    swarmFMResponse = requests.get("https://7tv.io/v3/emote-sets/01K1H87ZZVE92Y3Z37H3ES6BK8") #swarmfm
    if swarmFMResponse.status_code == 200:
        twitchEmotes.extend(swarmFMResponse.json()["emotes"])
    else:
        print("Failed to get swarmfm emotes")

    vedalResponse = requests.get("https://7tv.io/v3/emote-sets/01GN2QZDS0000BKRM8E4JJD3NV") #vedal987
    if vedalResponse.status_code != 200:
        raise Exception("Failed to get emotes")
    twitchEmotes.extend(vedalResponse.json()["emotes"])

    for emote in twitchEmotes:
        url = "https:" + emote["data"]["host"]["url"]
        emotes[emote["name"]] = url

def GetEmote(name):
    return emotes.get(name)