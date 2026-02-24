import re
import os
import glob
import io
import random
from enum import Enum
from requests.models import PreparedRequest
from requests.exceptions import MissingSchema
from ..utils import runcmd
from yt_dlp import YoutubeDL


class Stream(Enum):
    audio = 1
    video = 2


def get_cookies_file():
    folder_path = f"{os.getcwd()}/rbaqir"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file


yt_regex_str = (
    r"^((?:https?:)?\/\/)?"
    r"((?:www|m)\.)?"
    r"((?:youtube(-nocookie)?\.com|youtu.be))"
    r"(\/(?:[\w\-]+\?v=|embed\/|v\/)?)"
    r"([\w\-]+)(\S+)?$"
)
yt_regex = re.compile(yt_regex_str)


def check_url(url: str):
    prepared_request = PreparedRequest()
    try:
        prepared_request.prepare_url(url, None)
        return prepared_request.url
    except MissingSchema:
        return False


async def get_yt_stream_link(url: str, audio_only: bool = False) -> str:
    cookies = get_cookies_file()
    if audio_only:
        cmd = f'yt-dlp --cookies "{cookies}" --geo-bypass -f bestaudio -g "{url}"'
    else:
        cmd = f'yt-dlp --cookies "{cookies}" --geo-bypass -f bestvideo+bestaudio -g "{url}"'
    result = await runcmd(cmd)
    return result[0]


async def video_dl(url: str, title: str) -> str:
    os.makedirs("temp", exist_ok=True)
    path = os.path.join("temp", f"{title.replace(' ', '_')}.mp4")
    video_opts = {
        "format": "(bestvideo[height<=?360][ext=mp4])+(bestaudio[ext=m4a])",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": False,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
            {"key": "FFmpegMetadata"},
        ],
        "outtmpl": path,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "cookiefile": get_cookies_file(),
    }

    with YoutubeDL(video_opts) as ytdl:
        ytdl.extract_info(url)
    return path
