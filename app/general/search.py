from dataclasses import dataclass
from typing import Any

from features.song import Song


@dataclass
class SearchObject:
    id: Any
    value: str


def normalise(text: str):
    text = text.lower()
    for c in ",.'();":
        text = text.replace(c, "")

    return text.replace("_", " ")


def get_distance(value: str, query: str):
    m = len(query)
    n = len(value)

    table = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        table[i][0] = i

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if query[i - 1] == value[j - 1] else 1

            table[i][j] = min(
                table[i - 1][j] + 1,  # delete
                table[i][j - 1] + 1,  # insert
                table[i - 1][j - 1] + cost,  # match/substitute
            )

    return min(table[m])


def search(objects: list[SearchObject], query: str) -> list[SearchObject]:
    query = normalise(query)
    if len(query) == 0:
        return objects

    results = []
    for obj in objects:
        dist = get_distance(obj.value, query)
        sizediff = abs(len(query) - len(obj.value))

        total = dist * 1 + sizediff * 0.1
        results.append((total, obj))

    results.sort(key=lambda a: a[0])

    return [result[1] for result in results]


def search_songs(songs: list[Song], query: str) -> list[Song]:
    objects = []
    lookup = {}
    for song in songs:
        objects.append(SearchObject(song.id, normalise(song.title)))
        lookup[song.id] = song

    matches = search(objects, query)
    return [lookup[m.id] for m in matches]
