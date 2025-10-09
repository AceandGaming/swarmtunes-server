def SongEmbed(song):
    redirect_url = f"https://swarmtunes.com?song={song.uuid}"
    image_url = f"https://api.swarmtunes.com/covers/{song.uuid}?size=256"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{song.title} | SwarmTunes</title>

        <meta property="og:title" content="{song.title}" />
        <meta property="og:description" content="by {song.artist}\nCover by {song.cover_artist}" />
        <meta property="og:image" content="{image_url}" />
        <meta property="og:url" content="https://share.swarmtunes.com?song={song.uuid}" />
        <meta property="og:type" content="music.song" />

        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{song.title}" />
        <meta name="twitter:description" content="by {song.artist}" />
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