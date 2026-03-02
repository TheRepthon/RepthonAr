import re
import os
import glob
import time
import random
from yt_dlp import YoutubeDL


def get_cookies_file():
    folder_path = f"{os.getcwd()}/rbaqir"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file



yt_regex = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
)


YT_CACHE = {}


def _cache_valid(url: str):
    if url not in YT_CACHE:
        return False
    stream_url, expire = YT_CACHE[url]
    return time.time() < expire



async def get_stream(url: str, video: bool = False):

    if not yt_regex.match(url):
        return url

    if _cache_valid(url):
        return YT_CACHE[url][0]

    ydl_opts = {
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "cookiefile": get_cookies_file(),
        "js_runtimes": {
            "node": {}
        },
    }

    if video:
        ydl_opts["format"] = "best[height<=?720]"
    else:
        ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"

    with YoutubeDL(ydl_opts) as ytdl:
        info = ytdl.extract_info(url, download=False)

        if "entries" in info:
            info = info["entries"][0]

        stream_url = info["url"]

        YT_CACHE[url] = (stream_url, time.time() + 300)

        return stream_url



async def search_youtube(query: str):

    ydl_opts = {
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "default_search": "ytsearch1",
        "cookiefile": get_cookies_file(),
        "js_runtimes": {
            "node": {}
        },
    }

    with YoutubeDL(ydl_opts) as ytdl:
        info = ytdl.extract_info(query, download=False)

        if "entries" in info and info["entries"]:
            return info["entries"][0]["webpage_url"]

    return None
