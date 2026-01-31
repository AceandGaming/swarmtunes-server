from typing import Optional
from mutagen.id3 import ID3
from mutagen.id3._util import ID3NoHeaderError
import os
from pathlib import Path
import re
from datetime import datetime
from dataclasses import dataclass, field
import string
import json 

@dataclass
class AudioMetadata:
    title: Optional[str] = None
    titleTranslate: Optional[str] = None
    titleExtra: Optional[str] = None
    artists: list[str] = field(default_factory=lambda: [])
    singers: list[str] = field(default_factory=lambda: [])
    filetype: Optional[str] = None
    date: Optional[datetime] = None
    datetype: str = ""

    @property
    def MainTitle(self):
        return f"{self.titleTranslate or self.title}{self.titleExtra and f" ({self.titleExtra})" or ''}"

def FindSub(pattern, text):
    matches = re.findall(pattern, text)
    return re.sub(pattern, "", text), matches

def GetSingers(coverArtist):
    lower = coverArtist.lower()
    if "duet" in lower or ("neuro" in lower and "evil" in lower):
        return ["Neuro-sama", "Evil Neuro"]
    elif "evil" in lower:
        return  ["Evil Neuro"]
    elif "neuro" in lower:
        return  ["Neuro-sama"]
    else:
        return []

def MetadataFromFilename(filename):
    data = AudioMetadata(datetype="filename")


    filename, brakMatchs = FindSub(r"[\(\{\[].*?[\)\}\]]", filename)
    translate = None
    for match in brakMatchs:
        match = re.sub(r"[\[\{\(\)\}\]]*", "", match)
        lower = match.lower()

        date = re.search(r"(\d{2})[.\-_/ ](\d{2})[.\-_/ ](\d{2,4})", lower)
        singers = GetSingers(lower)
        if len(singers) > 0:
            data.singers = singers
        elif date:
            day, month, year = date.groups()
            year = int(year)
            if year < 100:
                year += 2000  # assuming 2000–2099
            try:
                data.date = datetime(year=year, month=int(month), day=int(day))
            except ValueError:
                pass
        elif re.match(r"^\d{4}$", match):
            try:
                data.date = datetime(year=int(match), month=12, day=19)
            except ValueError:
                pass
        elif re.match(r"^\D+$", match):
            translate = match

    filename = re.sub(r"^\d+\.", "", filename)
    filename, extention = FindSub(r"\..+?$", filename)
    if len(extention) > 0:
        data.filetype = extention[0].replace(".", "").upper()

    filename = filename.strip()
    group = re.match(r"(.*) - (.*)", filename)

    if group is None:
        data.title =  string.capwords(filename.strip())
    else:
        data.title = group.group(2).strip()

        artists = group.group(1).split(",")
        artists = [a.strip() for a in artists]
        data.artists = artists

    if translate is not None:
        if not re.match(r"^[a-zA-Z0-9_ \-.;:]+$", data.title or ""):
            data.titleTranslate = translate
        else:
            data.titleExtra = translate

    return data

def MetadataFromAudioData(path):
    data = AudioMetadata(datetype="audio")
    try:
        audio = ID3(path)
    except ID3NoHeaderError:
        return data
    
    # for key in audio.keys():
    #     try:
    #         print(key, audio[key].text[0])
    #     except:
    #         print(key)

    def GetTitleInfo(text):
        #title, match = FindSub(r"[\(\{\[]\D*?[\)\}\]]", text)
        title = text
        title = title.strip()
        titleExtra = None
        titleTranslate = None
        # if match:
        #     extra = re.sub(r"[\[\{\(\)\}\]]*", "", match[0])
        #     if not re.match(r"^[a-zA-Z0-9_ \-.;:]+$", title):
        #         titleTranslate = extra
        #     else:
        #         titleExtra = extra

        return title, titleExtra, titleTranslate

    if "COMM::ved" in audio:
        jsonData = json.loads(audio["COMM::ved"].text[0])
        if "Title" in jsonData:
            data.title, data.titleExtra, data.titleTranslate = GetTitleInfo(jsonData["Title"])
        if "Artist" in jsonData:
            artists = jsonData["Artist"].split(",")
            data.artists = [a.strip() for a in artists]
        if "CoverArtist" in jsonData:
            data.singers = GetSingers(jsonData["CoverArtist"])
        if "Date" in jsonData:
            try:
                data.date = datetime.fromisoformat(jsonData["Date"])
            except ValueError:
                print("Date error:", jsonData["Date"])

    if not data.title and "TIT2" in audio:
        data.title, data.titleExtra, data.titleTranslate = GetTitleInfo(audio["TIT2"].text[0])
    if not data.artists and "TPE1" in audio:
        group = re.match(r"(.*) - (.*)", audio["TPE1"].text[0])
        if group is not None:
            data.artists = group.group(2).split(",")
            data.artists = [a.strip() for a in data.artists]

            data.singers = GetSingers(
                group.group(1))
        else:
            data.artists = audio["TPE1"].text[0].split(",")
            data.artists = [a.strip() for a in data.artists]
    if not data.date:
        if "COMM::eng" in audio:
            text = audio["COMM::eng"].text[0]
            time = re.sub(r"//.*", "", text).strip()
            try:
                data.date = datetime.strptime(time, "%Y-%m-%d")
            except ValueError:
                print("Date error:", text)
        elif "TDRC" in audio:
            text = audio["TDRC"].text[0]
            try:
                data.date = datetime(year=int(str(text)), month=1, day=1)
                data.datetype = "year"
            except ValueError:
                pass
            
    return data

def MergeMetadata(audioData: AudioMetadata, nameData: AudioMetadata):

    data = AudioMetadata(
        title=audioData.title or nameData.title,
        titleExtra=audioData.titleExtra or nameData.titleExtra,
        titleTranslate=audioData.titleTranslate or nameData.titleTranslate,
        filetype=audioData.filetype or nameData.filetype
    )

    if len(audioData.artists) > 0:
        data.artists = audioData.artists
    else:
        data.artists = nameData.artists

    if len(audioData.singers) > 0:
        data.singers = audioData.singers
    else:
        data.singers = nameData.singers

    if audioData.date:
        if audioData.datetype == "year":
            if nameData.date:
                data.date = nameData.date
                data.datetype = nameData.datetype
            else:
                data.date = audioData.date
                data.datetype = audioData.datetype
        else:
            data.date = audioData.date
            data.datetype = audioData.datetype

    return data


def DeleteID3Tags(path):
    try:
        audio = ID3(path)
        audio.delete()
        audio.save()
    except ID3NoHeaderError:
        pass