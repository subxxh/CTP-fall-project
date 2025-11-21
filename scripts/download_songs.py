""" Helper script to download Youtube Videos or equivalent videos from soundcloud/spotify and convert to a .WAV file"""
import base64
import re
from pathlib import Path

import requests
from yt_dlp import YoutubeDL


# --- CONFIG ---
SPOTIFY_CLIENT_ID = "675c5ff0168c4157bbc6a419b0703647"
SPOTIFY_CLIENT_SECRET = "367277e14cc74c83a5e05ca8af63651c"
FFMPEG_PATH = "./ffmpeg/bin"

YDL_OPTS = {
    "format": "bestaudio/best",
    "ffmpeg_location": FFMPEG_PATH,
    "cookiesfrombrowser": ["firefox"],
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
    "js_runtimes": {"node": {}},
    "verbose": True,
    "compat_opts": set(),
    "remote_components": {"ejs:github"},
    "outtmpl": "uploads/%(title)s.%(ext)s",
}


# SPOTIFY METADATA
def get_spotify_metadata(track_url):
    credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    token_headers = {
        "Authorization": "Basic " + encoded,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers=token_headers,
    )

    if "access_token" not in r.json():
        return None

    token = r.json()["access_token"]

    match = re.search(r"track/([A-Za-z0-9]+)", track_url)
    if not match:
        return None

    track_id = match.group(1)
    auth = {"Authorization": f"Bearer {token}"}

    t = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=auth)
    data = t.json()

    return {"title": data["name"], "author": data["artists"][0]["name"]}


# SOUNDCLOUD METADATA
def get_soundcloud_metadata(track_url):
    with YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(track_url, download=False)
        return {"title": info["title"], "author": info["uploader"]}


# YOUTUBE SEARCH DOWNLOAD
def youtube_search_dl(query):
    with YoutubeDL(YDL_OPTS) as ydl:
        result = ydl.extract_info(f"ytsearch1:{query}", download=False)
    final_url = result["entries"][0]["webpage_url"]
    file_path = download_audio(final_url)
    return file_path, final_url


# MAIN DOWNLOAD LOGIC
def download_audio(url):
    """Download audio from URL or handle Spotify/SoundCloud links."""

    # Spotify
    if "spotify.com" in url:
        meta = get_spotify_metadata(url)
        if not meta:
            return None, None
        query = f"{meta['title']} {meta['author']} audio"
        return youtube_search_dl(query)

    # SoundCloud
    if "soundcloud.com" in url:
        meta = get_soundcloud_metadata(url)
        query = f"{meta['title']} {meta['author']} audio"
        return youtube_search_dl(query)

    # Direct YouTube / URL
    with YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
        final_url = info["webpage_url"]
        filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".wav"
        ydl.download([url])

    return Path("uploads") / Path(filename).name, final_url

