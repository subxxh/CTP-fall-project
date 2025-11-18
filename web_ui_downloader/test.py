import requests
from yt_dlp import YoutubeDL
import re
import base64

SPOTIFY_CLIENT_ID = "675c5ff0168c4157bbc6a419b0703647"
SPOTIFY_CLIENT_SECRET = "367277e14cc74c83a5e05ca8af63651c"
# TRACK_URL = "https://open.spotify.com/track/4FyesJzVpA39hbYvcseO2d?si=45bbc9df44de4a92"
FFMPEG_PATH = "./ffmpeg/bin"
YDL_OPTS = {
    "format": "bestaudio/best",
    "ffmpeg_location": FFMPEG_PATH,
    "cookiesfrombrowser": ["firefox"],
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    "js_runtimes": {"node": {}},
    # "extractor_args": {"youtube": {"player_client": "web"}},
    "verbose": True,
    "quiet": True,
    "compat_opts": set(),
    "remote_components": {"ejs:github"},
}


# credit: https://python.plainenglish.io/bored-of-libraries-heres-how-to-connect-to-the-spotify-api-using-pure-python-bd31e9e3d88a
# Use Spotify API to get track and artist names
def get_spotify_metadata(track_url):
    # Get Spotify auth token
    encoded_credentials = base64.b64encode(
        SPOTIFY_CLIENT_ID.encode() + b":" + SPOTIFY_CLIENT_SECRET.encode()
    ).decode("utf-8")
    token_headers = {
        "Authorization": "Basic " + encoded_credentials,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    token_data = {
        "grant_type": "client_credentials",
    }
    r = requests.post(
        "https://accounts.spotify.com/api/token", data=token_data, headers=token_headers
    )

    # Get track info
    token = r.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}
    # Extract ID from link, also handles extra tracking info if present
    id = (track_url.split("?", 1)[0]).split("k/")[1]
    t = requests.get(f"https://api.spotify.com/v1/tracks/{id}", headers=auth_header)
    d = t.json()
    return {"title": d["name"], "author": d["artists"][0]["name"]}


# Use youtubedyt_dlp to get track and artist names
def get_soundcloud_metadata(track_url):
    with YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(track_url, download=False)
        return {"title": info["title"], "author": info["uploader"]}


# Youtube search for song, then download first result
def youtube_search_dl(query):
    with YoutubeDL(YDL_OPTS) as ydl:
        result = ydl.extract_info(f"ytsearch1:{query}", download=False)
    url = result["entries"][0]["webpage_url"]
    filename = download_audio(url, FFMPEG_PATH)
    return f"Downloaded {filename} from URL: {url}"


# Download from URL
def download_audio(url, ffmpeg_path):
    with YoutubeDL(YDL_OPTS) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(info_dict).rsplit(".", 1)[0] + ".mp3"
        ydl.download([url])
    return filename


# --- main workflow ---
def main(TRACK_URL):
    if re.search("soundcloud", TRACK_URL):
        info = get_soundcloud_metadata(TRACK_URL)
        query = f"{info['title']} {info['author']} audio"
        return youtube_search_dl(query)

    elif re.search("spotify", TRACK_URL):
        info = get_spotify_metadata(TRACK_URL)
        query = f"{info['title']} {info['author']} audio"
        return youtube_search_dl(query)

    elif re.search("youtube", TRACK_URL):
        return download_audio(TRACK_URL, FFMPEG_PATH)

    else:
        return "Invalid URL!"


if __name__ == "__main__":
    result = main()
    if result:
        print("Downloaded file:", result)
