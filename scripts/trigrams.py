import scripts.search as search
import re
from typing import Dict, List, TypeAlias, Optional
from scripts.data_system import DataSystem
from scripts.types import Song

Trigrams: TypeAlias = Dict[str, List[search.Searchable]]

class TrigramStorage():
    trigrams = {}

    @classmethod
    def AddTrigrams(cls, label: str, trigrams: Trigrams):
        cls.trigrams[label] = trigrams
    @classmethod
    def GetTrigrams(cls, label: str):
        return cls.trigrams.get(label, [])

def GetTris(word: str):
    word = re.sub(r"[^a-z]", "", word.lower())
    tris = []
    for i in range(0, len(word) - 2):
        tris.append(word[i:i + 3])
    return tris

def CreateTrigrams(items: list[search.Searchable]):
    trigrams: Trigrams = {}
    for item in items:
        tris = GetTris(item.value)
        for tri in tris:
            if tri in trigrams:
                trigrams[tri].append(item)
            else:
                trigrams[tri] = [item]
    return trigrams
    
def Search(query: str, trigrams: Trigrams, mult: search.SearchMultipliers):
    tris = GetTris(query)
    items = set()
    for tri in tris:
        if tri in trigrams:
            items.update(trigrams[tri])
    return search.Search(query, list(items), mult)

def CreateSongTrigrams(songs: list[Song]):
    titleSearchables = [search.Searchable(song.title, song.id) for song in songs]
    artistSearchables = [search.Searchable(song.artist, song.id) for song in songs]
    trigrams = CreateTrigrams(titleSearchables + artistSearchables)
    TrigramStorage.AddTrigrams("songs", trigrams)
    return trigrams

def SearchSongs(query: str, songs: Optional[list[Song]] = None, multipliers: Optional[search.SearchMultipliers] = None):
    if len(query) < 3:
        return search.SearchSongs(query, songs, multipliers)
    if not query.strip():
        return DataSystem.songs.items
    if not multipliers:
        multipliers = search.SearchMultipliers()
    if not songs:
        songs = DataSystem.songs.items
    trigrams = TrigramStorage.GetTrigrams("songs")
    if trigrams == []:
        trigrams = CreateSongTrigrams(songs)
        
    matches = Search(query, trigrams, multipliers)
    if matches == {}:
        return DataSystem.songs.items
    ids = search.SortSearch(matches)
    songs = DataSystem.songs.GetList(ids)
    return songs