from features.song import Song

def _create_embed(title: str, description: str, image: str, redirect: str):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{title} | SwarmTunes</title>

        <meta property="og:title" content="{title}" />
        <meta property="og:description" content="{description}" />
        <meta property="og:image" content="{image}" />
        <meta property="og:url" content="{redirect}" />
        <meta property="og:type" content="music.song" />

        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{title}" />
        <meta name="twitter:description" content="{description}" />
        <meta name="twitter:image" content="{image}" />
    </head>
    <body>
        <script>
            window.location.href = "{redirect}";
        </script>
        <p>Redirecting to <a href="{redirect}">{redirect}</a>...</p>
    </body>
    </html>
    """

def create_song_embed(song: Song):
    redirect_url = f"https://swarmtunes.com?song={song.id}"
    image_url = f"https://api.swarmtunes.com/covers/{song.coverArt}"
    
    return _create_embed(
        title = song.title,
        description = f"""
        Artists: {', '.join([artist.name for artist in song.artists])}
        Covered by: {', '.join([artist.name for artist in song.singers])}
        {song.date_released.strftime("%d/%m/%Y")}
        """,
        image = image_url,
        redirect = redirect_url
    )