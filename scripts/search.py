from dataclasses import dataclass
import re
import math
from scripts.data_system import DataSystem
from scripts.types import Song
from typing import Optional
from datetime import datetime

@dataclass
class SearchMultipliers:
    wordDiff = 3
    lengthDiff = 0.2
    recentcy = 0.0001
    caseDiff = 0.03
    order = 12
    exactness = 0.22

@dataclass
class Searchable():
    value: str
    id: str
    date: Optional[datetime] = None
    def __hash__(self) -> int:
        return hash(self.id + self.value)

def SplitAll(string: str):
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+', string)

def Match(queryWord: str, itemWord: str):
    if queryWord == itemWord:
        return 0, 0
    wordDiff = 0
    caseDiff = 0
    for queryChar, itemChar in zip(queryWord, itemWord):
        if queryChar.lower() != itemChar.lower():
            wordDiff += 1
        else:
            if queryChar != itemChar:
                caseDiff += 1
    minimum = min(len(queryWord), len(itemWord))
    wordDiff += max(0, len(queryWord) - len(itemWord))
    return wordDiff / minimum, caseDiff / minimum

def MatchEqualWords(queryWords: list[str], itemWords: list[str]):
    wordDiff = 0
    caseDiff = 0
    count = len(itemWords)
    for i in range(0, count):
        diff = Match(queryWords[i], itemWords[i])
        wordDiff += diff[0]
        caseDiff += diff[1]
    return wordDiff / count, caseDiff / count

def MatchUnequalWords(queryWords: list[str], itemWords: list[str]):
    wordDiffTotal = 0
    caseDiffTotal = 0
    for itemWord in itemWords:
        wordDiff = math.inf
        caseDiff = math.inf
        for queryWord in queryWords:
            diff = Match(queryWord, itemWord)
            if diff[0] < wordDiff:
                wordDiff = diff[0]
                caseDiff = diff[1]
                if wordDiff == 0:
                    return 0, 0
        wordDiffTotal += wordDiff
        caseDiffTotal += caseDiff
    return wordDiffTotal / len(itemWords), caseDiffTotal / len(itemWords)

def MatchOrder(queryWords: list[str], itemWords: list[str]):
    order = 0
    try:
        startPos = itemWords.index(queryWords[0])
    except ValueError:
        return 0
    for i in range(1, len(queryWords)):
        if startPos + i >= len(itemWords):
            break
        if queryWords[i] == itemWords[startPos + i]:
            order += 1
    return order / len(queryWords)

def Search(query: str, items: list[Searchable], mult: SearchMultipliers):
    queryWords = SplitAll(query)
    matches: dict[str, float] = {}
    if len(query) == 0:
        return matches
    for item in items:
        if item.value == "":
            continue
        item.value = item.value.replace("(", "").replace(")", "")
        itemWords = item.value.split()
        if len(itemWords) < len(queryWords):
            continue
        if Match(query, item.value)[0] / len(query) > 1 - mult.exactness:
            continue

        lengthDiff = abs(len(queryWords) - len(itemWords))

        wordDiff, caseDiff = 0, 0
        if mult.exactness < 1:
            if len(itemWords) == len(queryWords):
                wordDiff, caseDiff = MatchEqualWords(queryWords, itemWords)
            else:
                wordDiff, caseDiff = MatchUnequalWords(queryWords, itemWords)
        
        
        order = MatchOrder(queryWords, itemWords)
        dayOffset = 0
        if item.date:
            dayOffset = (datetime.now() - item.date).days

        totalDiff = lengthDiff * mult.lengthDiff + wordDiff * mult.wordDiff + caseDiff * mult.caseDiff - order * mult.order + dayOffset * mult.recentcy
        matches[item.id] = min(totalDiff, matches.get(item.id, math.inf))

    return matches

def SortSearch(matches):
    sorted = []
    for item in matches:
        sorted.append((item, matches[item]))
    sorted.sort(key=lambda item: item[1])
    median = sorted[len(sorted) // 2][1]
    max = sorted[0][1]
    culled = [item[0] for item in sorted if item[1] <= (max + median) / 2.2]
    return culled

def SearchSongs(query: str, songs: Optional[list[Song]] = None, multipliers: Optional[SearchMultipliers] = None):
    if not query.strip():
        return DataSystem.songs.items
    if not multipliers:
        multipliers = SearchMultipliers()
    if not songs:
        songs = DataSystem.songs.items
    titleSearchables = [Searchable(song.title, song.id, song.date) for song in songs]
    artistSearchables = [Searchable(song.prettyArtists, song.id, song.date) for song in songs]
    matches = Search(query, titleSearchables + artistSearchables, multipliers)
    if matches == {}:
        return DataSystem.songs.items
    ids = SortSearch(matches)
    songs = DataSystem.songs.GetList(ids)
    return songs