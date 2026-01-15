from scripts.types import Song, Playlist
from scripts.serializer import PlaylistSerializer

def SongEmbed(song: Song):
    redirect_url = f"https://swarmtunes.com?song={song.id}"
    image_url = f"https://api.swarmtunes.com/covers/{song.cover}"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{song.title} | SwarmTunes</title>

        <meta property="og:title" content="{song.title}" />
        <meta property="og:description" content="Artist: {song.artist}\nSung by: {", ".join(song.singers)}" />
        <meta property="og:image" content="{image_url}" />
        <meta property="og:url" content="https://share.swarmtunes.com?song={song.id}" />
        <meta property="og:type" content="music.song" />

        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{song.title}" />
        <meta name="twitter:description" content="Artist: {song.artist}" />
        <meta name="twitter:image" content="{image_url}" />
    </head>
    <body>
        <script>
            window.location.href = "{redirect_url}";
        </script>
        <p>Redirecting to <a href="{redirect_url}">{redirect_url}</a>...</p>
    </body>
    </html>
    """

def PlaylistEmbed(playlist: Playlist, shareCode: str):
    redirect_url = f"https://swarmtunes.com?playlist={shareCode}"
    image_url = f"https://api.swarmtunes.com/covers/{playlist.coverType}?size=256"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{playlist.name} | SwarmTunes</title>

        <meta property="og:title" content="{playlist.name}" />
        <meta property="og:description" content="Created on: {playlist.date.strftime("%d %B %Y")}\n{len(playlist.songIds)} songs" />
        <meta property="og:image" content="{image_url}" />
        <meta property="og:url" content="https://share.swarmtunes.com?p={shareCode}" />
        <meta property="og:type" content="music.playlist" />

        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{playlist.name}" />
        <meta name="twitter:description" content="Created on: {playlist.date.strftime("%d %B %Y")}\n{len(playlist.songIds)} songs" />
        <meta name="twitter:image" content="{image_url}" />
    </head>
    <body>
        <script>
            window.location.href = "{redirect_url}";
        </script>
        <p>Redirecting to <a href="{redirect_url}">{redirect_url}</a>...</p>
    </body>
    </html>
    """