from scripts.types import Song
from datetime import datetime
from typing import Optional
from scripts.data_system import DataSystem

class SearchMultipliers:
    def __init__(self, lengthDiffrence = 1, charDiffrence = 80, relevancy = 0.02):
        self.lengthDiffrence = lengthDiffrence
        self.charDiffrence = charDiffrence
        self.relevancy = relevancy

def ScoreSong(song: Song, query: str, multipliers: Optional[SearchMultipliers] = None):
    if not multipliers:
        multipliers = SearchMultipliers()
    query = query.lower()
    title = song.title.lower()
    artist = song.artist.lower()

    lengthDiffrence = abs(len(title) - len(query))
    titleDiffrence = 0
    artistDiffrence = 0
    for i, char in enumerate(query):
        if i < len(title):
            if char != title[i]:
                titleDiffrence += 1
        else:
            titleDiffrence += 1
        if i < len(artist):
            if char != artist[i]:
                artistDiffrence += 1
        else:
            artistDiffrence += 1
    titleDiffrence /= len(query)
    artistDiffrence /= len(query)
    if artist == "":
        artistDiffrence = len(query)
    relevancy = (datetime.now() - song.date).days
    if relevancy > 100:
        relevancy = 100
    return lengthDiffrence * multipliers.lengthDiffrence + min(titleDiffrence, artistDiffrence) * multipliers.charDiffrence + relevancy * multipliers.relevancy

def SearchSongs(query, multipliers: Optional[SearchMultipliers] = None):
    if query == "":
        return sorted(DataSystem.songs.items, key=lambda song: song.date, reverse=True)
    if not multipliers:
        multipliers = SearchMultipliers()
    return sorted(DataSystem.songs.items, key=lambda song: ScoreSong(song, query, multipliers))