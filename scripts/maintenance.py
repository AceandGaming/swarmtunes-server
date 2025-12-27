from scripts.data_system import DataSystem
from scripts.types import *
import scripts.paths as paths
from scripts.delete import DeleteManager


def ClearOrphanedSongs():
    songFileIds: set[str] = set()
    mp3FileIds: set[str] = set()

    for file in paths.MP3_DIR.iterdir():
        mp3FileIds.add(file.name)
    for file in paths.SONGS_DIR.iterdir():
        songFileIds.add(file.name)

    if len(songFileIds) == 0 or len(mp3FileIds) == 0:
        raise Exception("Failed check before clearing orphaned songs")

    allIds = songFileIds | mp3FileIds

    for id in allIds:
        inSongFile = id in songFileIds
        inMp3File = id in mp3FileIds
        
        if inSongFile and inMp3File:
            continue

        if inSongFile and not inMp3File:
            print(f"Deleting orphaned song: {id}")
            DeleteManager.DeleteFile(paths.SONGS_DIR / id)
            continue

        if not inSongFile and inMp3File:
            print(f"Deleting orphaned mp3: {id}")
            DeleteManager.DeleteFile(paths.MP3_DIR / id)
            continue

def ClearOrphanedPlaylists():
    playlists = set([playlist.id for playlist in DataSystem.playlists.items])
    userPlaylists = set()
    userLookup: dict[str, User] = {}

    for user in DataSystem.users.items:
        ids = user.userData.playlistIds or []
        userPlaylists |= set(ids)
        for id in ids:
            userLookup[id] = user

    if (len(userPlaylists) == 0) ^ (len(playlists) == 0):
        raise Exception("Failed check before clearing orphaned playlists")

    all = userPlaylists | playlists

    for id in all:
        if id not in playlists:
            print(f"Removing orphaned link to playlist: {id}")
            uPlaylists = userLookup[id].userData.playlistIds
            if uPlaylists is not None:
                uPlaylists.remove(id)
            DataSystem.users.Save(userLookup[id])

        if id not in userPlaylists:
            print(f"Deleting orphaned playlist: {id}")
            DataSystem.playlists.RemoveById(id)
            
def ClearOrphanedTokens():
    for token in DataSystem.tokens.items:
        if DataSystem.users.Get(token.userId) is None:
            print(f"Deleting orphaned token: {token.id}")
            DataSystem.tokens.Remove(token)
        
def ClearOrphanedLinksToSongs():
    for playlist in DataSystem.playlists.items:
        playlist.songIds = [song.id for song in playlist.songs] #works because None values aren't added to playlist.songs
        DataSystem.playlists.Save(playlist)
    
    for album in DataSystem.albums.items:
        album.songIds = set([song.id for song in album.songs]) #same as above
        if len(album.songIds) == 0:
            print(f"Deleting album with no vaild songs: {album.id}")
            DataSystem.albums.Remove(album)
        else:
            DataSystem.albums.Save(album)

def ClearAllOrphaned():
    ClearOrphanedSongs()
    ClearOrphanedPlaylists()
    ClearOrphanedTokens()
    ClearOrphanedLinksToSongs()

def ClearProcessing():
    count = 0
    for file in paths.PROCESSING_DIR.iterdir():
        file.unlink()
        count += 1
    print(f"Deleted {count} files from processing")
