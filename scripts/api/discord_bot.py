import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import google_drive
from songs import *

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

currentSong = {}
editing = False
aproveAllSongs = False
                                        
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# @bot.command()
# async def title(ctx, *prams):
#     global currentSong
#     newTitle = " ".join(prams)
#     if not editing:
#         await ctx.send("Command not vaild at current time")
#         return
#     currentSong["title"] = newTitle
#     await ctx.send(f"Updated title to '{newTitle}'")

# @bot.command()
# async def artist(ctx, *prams):
#     global currentSong
#     newArtist = " ".join(prams)
#     if not editing:
#         await ctx.send("Command not vaild at current time")
#         return
#     currentSong["artist"] = newArtist
#     await ctx.send(f"Updated artist to '{newArtist}'")

# @bot.command()
# async def type(ctx, newType):
#     global currentSong
#     if not editing:
#         await ctx.send("Command not vaild at current time")
#         return
#     if newType.lower() not in ["neuro", "evil", "duet"]:
#         await ctx.send("Invaild type. Type must be 'neuro', 'evil' or 'duet'")
#         return
#     currentSong["type"] = newType
#     await ctx.send(f"Updated type to '{newType}'")

# @bot.command()
# async def date(ctx, *prams):
#     global currentSong
#     newDate = " ".join(prams)
#     if not editing:
#         await ctx.send("Command not vaild at current time")
#         return
#     currentSong["date"] = newDate
#     await ctx.send(f"Updated date to '{newDate}'")

@bot.command()
async def confirm(ctx):
    global editing
    editing = False

@bot.command()
async def aproveall(ctx):
    global aproveAllSongs
    aproveAllSongs = True

# @bot.command() 
# async def show(ctx):
#     await ctx.send(embed=EmbedSong(currentSong))

# def EmbedSong(song, orignalName=None, uuid=None, colour=0x00ffcc):
#     discString = f'Date: {song["date"]}\nType: {song["type"]}\n\nGoogle Drive ID: {song["google_drive_id"]}'
#     if orignalName is not None:
#         discString += f"\nFile Name: {orignalName}"
#     if uuid is not None:
#         discString += f"\n\nuuid: {uuid}"
#     embed = discord.Embed(
#         title=f'{song["title"]} by {song["artist"]}',
#         description=discString,
#         color=colour
#     )
#     return embed

# async def EditSong(ctx, song):
#     global currentSong, editing
#     currentSong = song
#     editing = True
#     await ctx.send("To edit a peramitor type '!' followed by it's name. To confirm type '!confirm'")
#     while editing:
#         await asyncio.sleep(0.1)
#     await ctx.send(embed=EmbedSong(song, None, None, 0x00ff00))
#     editing = False
#     return currentSong

# async def ListSongs(ctx, songs):
#     def make_edit_callback(song, uuid):
#         async def edit_callback(interaction):
#             await interaction.response.defer()
#             newSong = await EditSong(ctx, song)
#             SongManager.UpdateSong(uuid, Song.CreateFromDict(newSong, uuid))
#             await ctx.send("Don't forget to save!")
#         return edit_callback
#     for song in songs:
#         embed = EmbedSong(song, None, song.uuid)
    
#         edit_button = Button(label="Edit", style=discord.ButtonStyle.blurple)
#         edit_button.callback = make_edit_callback(song, song.uuid)

#         view = View()
#         view.add_item(edit_button)
    
#         await ctx.send(embed=embed, view=view)

# async def ApproveSong(ctx, song, orignalName):
#     embed = EmbedSong(song, orignalName)
#     reaction = 0
#     approve_button = Button(label="Approve", style=discord.ButtonStyle.green)
#     edit_button = Button(label="Edit", style=discord.ButtonStyle.blurple)

#     async def approve_callback(interaction):
#         nonlocal reaction
#         reaction = 1
#         await interaction.response.defer()
#     async def edit_callback(interaction):
#         nonlocal reaction
#         reaction = 2
#         await interaction.response.defer()

#     approve_button.callback = approve_callback
#     edit_button.callback = edit_callback

#     view = View()
#     view.add_item(approve_button)
#     view.add_item(edit_button)

#     await ctx.send(embed=embed, view=view)
#     while True:
#         if reaction == 1 or aproveAllSongs:
#             return currentSong
#         if reaction == 2:
#             return await EditSong(ctx, song)
#         await asyncio.sleep(0.1)
    
# @bot.command()
# async def resync(ctx):
#     global aproveAllSongs
#     message = await ctx.send("Loading...")
    
#     await message.edit(content="Indexing...")
#     files = google_drive.GetAllFiles()
#     await message.edit(content="Downloading...")
#     aproveAllSongs = True #False
#     songs = []
#     for i, file in enumerate(files):
#         if SongManager.GetSongWithGoogleDriveID(file["id"]) is not None:
#             continue
#         print(f"Downloading '{file["name"]}' {i}/{len(files)}. ID: {file["id"]}")
#         downloadTask = asyncio.create_task(google_drive.DownloadFile(file["id"]))

#         songData = google_drive.GenerateMetaDataFromFile(file["name"])
#         songData["type"] = file["folder"]
#         songData["google_drive_id"] = file["id"]

#         if aproveAllSongs:
#             aprovedSongData = songData
#         else:
#             await ctx.send(f"{i+1}/{len(files)}")
#             # aprovedSongData = await ApproveSong(ctx, songData, file["name"])
#         await downloadTask
#         song = Song(aprovedSongData["title"], aprovedSongData["type"], aprovedSongData["artist"], aprovedSongData["date"], file["id"])
#         song.AttachFile()
#         SongManager.AddSong(song)
#         songs.append(song)
#         if i % 10 == 5:
#             SongManager.Save()
#     AlbumManager.AddSongs(songs)
#     SongManager.Save()
#     AlbumManager.Save()
#     await ctx.send("Complete!")
# @bot.command()
# async def regeneratealbums(ctx):
#     AlbumManager.RegenerateAlbums()
#     AlbumManager.Save()
#     await ctx.send("Complete!")
# @bot.command()
# async def save(ctx):
#     SongManager.Save()
#     AlbumManager.Save()
#     await ctx.send("Saved!")
# @bot.command()
# async def find(ctx, *prams):
#     name = " ".join(prams).lower()
#     songs = SongManager.Search(name)
#     await ListSongs(ctx, songs)

# @bot.command()
# async def findartist(ctx, *prams):
#     artist = " ".join(prams).lower()
#     songs = SongManager.Search(artist, "artist")
#     await ListSongs(ctx, songs)

# @bot.command()
# async def get(ctx, uuid):
#     song = SongManager.GetSong(uuid)
#     if song is None:
#         await ctx.send("File not found")
#         return
#     await ctx.send("http://serverland:8000/songs/file/")
#     await ListSongs(ctx, {uuid: song})

# @bot.command()
# async def songcount(ctx):
#     await ctx.send(len(SongManager.GetSongs(True)))

async def RunBot():
    await bot.start("MTM5Nzg4NzgzMzM1MTY1NTQ1NA.GxaWtC._tG7oZ-2fO8l3NipLrqHQzlr7k6Itm1OZVt7Fc")