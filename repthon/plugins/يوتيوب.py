import asyncio
import glob
import contextlib
import io
import os
import re
import pathlib
from time import time
import requests
import random
from pathlib import Path

import aiohttp
import aiofiles
import wget
import yt_dlp
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from ShazamAPI import Shazam
from validators.url import url

from urlextract import URLExtract
from wget import download
from yt_dlp import YoutubeDL
from yt_dlp.utils import (
    ContentTooShortError,
    DownloadError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

from telethon import events
from telethon.tl import types
from telethon.utils import get_attributes
from telethon.errors.rpcerrorlist import YouBlockedUserError, ChatSendMediaForbiddenError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.tl.types import DocumentAttributeAudio

from ..Config import Config
from ..core import pool
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import progress, reply_id
from ..helpers.functions import delete_conv, name_dl, song_dl, video_dl, yt_search
from ..helpers.functions.utube import _mp3Dl, get_yt_video_id, get_ytthumb, ytsearch
from ..helpers.tools import media_type
from ..helpers.utils import _format, reply_id, _reputils
from . import BOTLOG, BOTLOG_CHATID, zq_lo

BASE_YT_URL = "https://www.youtube.com/watch?v="
extractor = URLExtract()
LOGS = logging.getLogger(__name__)

plugin_category = "البحث"

# =========================================================== #
#                                                             
# =========================================================== #
SONG_SEARCH_STRING = "<b>╮ جـارِ البحث ؏ـن المقطـٓع الصٓوتـي... 🎧♥️╰</b>"
SONG_NOT_FOUND = "<b>⎉╎لـم استطـع ايجـاد المطلـوب .. جرب البحث باستخـدام الامـر (.اغنيه)</b>"
SONG_SENDING_STRING = "<b>╮ جـارِ تحميـل المقطـٓع الصٓوتـي... 🎧♥️╰</b>"
# =========================================================== #
#                                                             
# =========================================================== #


def get_cookies_file():
    folder_path = f"{os.getcwd()}/rbaqir"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file


video_opts = {
    # Try separate video+audio first, then fall back to a single-file format.
    "format": "bv*+ba/b",
    "outtmpl": "rep_ytv.%(ext)s",
    "merge_output_format": "mp4",
    "noplaylist": True,
    "geo_bypass": True,
    "quiet": True,
    "no_warnings": True,
    "prefer_ffmpeg": True,
    "cookiefile": get_cookies_file(),
    "js_runtimes": {"node": {}},
}


async def ytdl_down(event, opts, url):
    ytdl_data = None
    try:
        await event.edit("**╮ ❐ يتـم جلـب البيانـات انتظـر قليلاً ...𓅫╰▬▭ **")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await event.edit(f"`{DE}`")
    except ContentTooShortError:
        await event.edit("**- عذرا هذا المحتوى قصير جدا لتنزيله ⚠️**")
    except GeoRestrictedError:
        await event.edit(
            "**- الفيديو غير متاح من موقعك الجغرافي بسبب القيود الجغرافية التي يفرضها موقع الويب ❕**"
        )
    except MaxDownloadsReached:
        await event.edit("**- تم الوصول إلى الحد الأقصى لعدد التنزيلات ❕**")
    except PostProcessingError:
        await event.edit("**كان هناك خطأ أثناء المعالجة**")
    except UnavailableVideoError:
        await event.edit("**⌔∮عـذرًا .. الوسائط غير متوفـره بالتنسيق المطلـوب**")
    except XAttrMetadataError as XAME:
        await event.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    except ExtractorError:
        await event.edit("**حدث خطأ أثناء استخراج المعلومات يرجى وضعها بشكل صحيح ⚠️**")
    except Exception as e:
        await event.edit(f"**- خطـأ : **\n__{e}__")
    return ytdl_data


async def fix_attributes(
    path, info_dict: dict, supports_streaming: bool = False, round_message: bool = False
) -> list:
    """Avoid multiple instances of an attribute."""
    new_attributes = []
    video = False
    audio = False

    uploader = info_dict.get("uploader", "Unknown artist")
    duration = int(info_dict.get("duration", 0))
    suffix = path.suffix[1:]
    if supports_streaming and suffix != "mp4":
        supports_streaming = True

    attributes, mime_type = get_attributes(path)
    if suffix == "mp3":
        title = str(info_dict.get("title", info_dict.get("id", "Unknown title")))
        audio = types.DocumentAttributeAudio(
            duration=duration, voice=None, title=title, performer=uploader
        )
    elif suffix == "mp4":
        width = int(info_dict.get("width", 0))
        height = int(info_dict.get("height", 0))
        for attr in attributes:
            if isinstance(attr, types.DocumentAttributeVideo):
                duration = duration or attr.duration
                width = width or attr.w
                height = height or attr.h
                break
        video = types.DocumentAttributeVideo(
            duration=duration,
            w=width,
            h=height,
            round_message=round_message,
            supports_streaming=supports_streaming,
        )

    if audio and isinstance(audio, types.DocumentAttributeAudio):
        new_attributes.append(audio)
    if video and isinstance(video, types.DocumentAttributeVideo):
        new_attributes.append(video)

    new_attributes.extend(
        attr
        for attr in attributes
        if (
            isinstance(attr, types.DocumentAttributeAudio)
            and not audio
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not video
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not isinstance(attr, types.DocumentAttributeVideo)
        )
    )
    return new_attributes, mime_type


@zq_lo.rep_cmd(pattern="سناب(?: |$)(.*)")
async def download_video(event):
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    revent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        ytdl_data = await ytdl_down(revent, video_opts, url)
        if ytdl_data is None:
            return
        try:
            f = pathlib.Path("rep_ytv.mp4")
            print(f)
            catthumb = pathlib.Path("rep_ytv.jpg")
            if not os.path.exists(catthumb):
                catthumb = pathlib.Path("rep_ytv.webp")
            if not os.path.exists(catthumb):
                catthumb = None
            await revent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{ytdl_data['title']}**"
            )
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                f, ytdl_data, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, revent, c_time, "Upload :", file_name=ytdl_data["title"]
                    )
                ),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            await event.client.send_file(
                event.chat_id,
                file=media,
                reply_to=reply_to_id,
                caption=f'**⎉╎المقطــع :** `{ytdl_data["title"]}`\n**⎉╎الرابـط : {msg}**\n**⎉╎تم  التحميـل .. بنجـاح ✅**"',
                thumb=catthumb,
            )
            os.remove(f)
            if catthumb:
                os.remove(catthumb)
        except TypeError:
            await asyncio.sleep(2)
    await event.delete()


@zq_lo.rep_cmd(pattern="فيس(?: |$)(.*)")
async def download_video_facebook(event):
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    revent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        ytdl_data = await ytdl_down(revent, video_opts, url)
        if ytdl_data is None:
            return
        try:
            f = pathlib.Path("rep_ytv.mp4")
            print(f)
            catthumb = pathlib.Path("rep_ytv.jpg")
            if not os.path.exists(catthumb):
                catthumb = pathlib.Path("rep_ytv.webp")
            if not os.path.exists(catthumb):
                catthumb = None
            await revent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{ytdl_data['title']}**"
            )
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                f, ytdl_data, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, revent, c_time, "Upload :", file_name=ytdl_data["title"]
                    )
                ),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            await event.client.send_file(
                event.chat_id,
                file=media,
                reply_to=reply_to_id,
                caption=f'**⎉╎المقطــع :** `{ytdl_data["title"]}`\n**⎉╎الرابـط : {msg}**\n**⎉╎تم  التحميـل .. بنجـاح ✅**"',
                thumb=catthumb,
            )
            os.remove(f)
            if catthumb:
                os.remove(catthumb)
        except TypeError:
            await asyncio.sleep(2)
    await event.delete()


@zq_lo.rep_cmd(pattern="بنترست(?: |$)(.*)")
async def download_video_pintrest(event):
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    revent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        ytdl_data = await ytdl_down(revent, video_opts, url)
        if ytdl_data is None:
            return
        try:
            f = pathlib.Path("rep_ytv.mp4")
            print(f)
            catthumb = pathlib.Path("rep_ytv.jpg")
            if not os.path.exists(catthumb):
                catthumb = pathlib.Path("rep_ytv.webp")
            if not os.path.exists(catthumb):
                catthumb = None
            await revent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{ytdl_data['title']}**"
            )
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                f, ytdl_data, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, revent, c_time, "Upload :", file_name=ytdl_data["title"]
                    )
                ),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            await event.client.send_file(
                event.chat_id,
                file=media,
                reply_to=reply_to_id,
                caption=f'**⎉╎المقطــع :** `{ytdl_data["title"]}`\n**⎉╎الرابـط : {msg}**\n**⎉╎تم  التحميـل .. بنجـاح ✅**"',
                thumb=catthumb,
            )
            os.remove(f)
            if catthumb:
                os.remove(catthumb)
        except TypeError:
            await asyncio.sleep(2)
    await event.delete()


@zq_lo.rep_cmd(
    pattern="ساوند(?: |$)(.*)",
    command=("ساوند", plugin_category),
    info={
        "header": "تحميـل الاغـاني مـن سـاونـد كـلاود الـخ عـبر الرابـط",
        "مثــال": ["{tr}ساوند بالــرد ع رابــط", "{tr}ساوند + رابــط"],
    },
)
async def download_audio_sound_cloud(event):
    """To download audio from YouTube and many other sites."""
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    revent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        try:
            vid_data = YoutubeDL({"no-playlist": True, "cookiefile": get_cookies_file()}).extract_info(
                url, download=False
            )
        except ExtractorError:
            vid_data = {"title": url, "uploader": "Catuserbot", "formats": []}
        startTime = time()
        retcode = await _mp3Dl(url=url, starttime=startTime, uid="320")
        if retcode != 0:
            return await event.edit(str(retcode))
        _fpath = ""
        thumb_pic = None
        for _path in glob.glob(os.path.join(Config.TEMP_DIR, str(startTime), "*")):
            if _path.lower().endswith((".jpg", ".png", ".webp")):
                thumb_pic = _path
            else:
                _fpath = _path
        if not _fpath:
            return await edit_delete(zedevent, "__Unable to upload file__")
        await revent.edit(
            f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
            \n**{vid_data['title']}***"
        )
        attributes, mime_type = get_attributes(str(_fpath))
        ul = io.open(pathlib.Path(_fpath), "rb")
        if thumb_pic is None:
            thumb_pic = str(
                await pool.run_in_thread(download)(
                    await get_ytthumb(get_yt_video_id(url))
                )
            )
        uploaded = await event.client.fast_upload_file(
            file=ul,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    revent,
                    startTime,
                    "trying to upload",
                    file_name=os.path.basename(pathlib.Path(_fpath)),
                )
            ),
        )
        ul.close()
        media = types.InputMediaUploadedDocument(
            file=uploaded,
            mime_type=mime_type,
            attributes=attributes,
            force_file=False,
            thumb=await event.client.upload_file(thumb_pic) if thumb_pic else None,
        )
        await event.client.send_file(
            event.chat_id,
            file=media,
            caption=f"<b>⎉╎المقطع : </b><code>{vid_data.get('title', os.path.basename(pathlib.Path(_fpath)))}</code>",
            supports_streaming=True,
            reply_to=reply_to_id,
            parse_mode="html",
        )
        for _path in [_fpath, thumb_pic]:
            os.remove(_path)
    await zedevent.delete()


@zq_lo.rep_cmd(
    pattern="يوتيوب(?: |$)(\\d*)? ?([\\s\\S]*)",
    command=("يوتيوب", plugin_category),
    info={
        "header": "لـ البحـث عـن روابــط بالكلمــه المحــدده علـى يـوتيــوب",
        "مثــال": [
            "{tr}يوتيوب + كلمـه",
            "{tr}يوتيوب + عدد + كلمـه",
        ],
    },
)
async def yt_search(event):
    "Youtube search command"
    if event.is_reply and not event.pattern_match.group(2):
        query = await event.get_reply_message()
        query = str(query.message)
    else:
        query = str(event.pattern_match.group(2))
    if not query:
        return await edit_delete(
            event, "**╮ بالـرد ﮼؏ كلمـٓھہ للبحث أو ضعها مـع الأمـر ... 𓅫╰**"
        )
    video_q = await edit_or_reply(event, "**╮ جـارِ البحث ▬▭... ╰**")
    if event.pattern_match.group(1) != "":
        lim = int(event.pattern_match.group(1))
        if lim <= 0:
            lim = int(10)
    else:
        lim = int(10)
    try:
        full_response = await ytsearch(query, limit=lim)
    except Exception as e:
        return await edit_delete(video_q, str(e), time=10, parse_mode=_format.parse_pre)
    reply_text = f"**⎉╎اليك عزيزي قائمة بروابط الكلمة اللتي بحثت عنها:**\n`{query}`\n\n**⎉╎النتائج:**\n{full_response}"
    await edit_or_reply(video_q, reply_text)

# ================================================================================================ #
# =========================================ساوند كلاود================================================= #
# ================================================================================================ #

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


#R
@zq_lo.rep_cmd(pattern="بحث(?: |$)(.*)")
async def _(event): #Code by T.me/RR0RT
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
    elif reply and reply.message:
        query = reply.message
    else:
        return await edit_or_reply(event, "**⎉╎قم باضافـة إسـم للامـر ..**\n**⎉╎بحث + اسـم المقطـع الصـوتي**")
    revent = await edit_or_reply(event, "** ╮ جـارِ البحث ؏ـن المقطـٓع الصٓوتـي... 🎧♥️╰ **")
    
    audio_file = None
    thumb_name = None

    try:
        results = await asyncio.to_thread(
            lambda: YoutubeSearch(query, max_results=1).to_dict()
        )

        if not results:
            return await revent.edit("**• لم يتم العثور على أي نتيجة ✖️**")

        result = results[0]
        link = f"https://youtube.com{result['url_suffix']}"
        title = result.get("title", "Audio")[:40]
        duration_text = result.get("duration") or "0:00"

    except Exception as e:
        return await revent.edit(
            f"**• فشـل في البحث**\n**• الخطـأ :** `{str(e)}`"
        )

    await revent.edit("**╮ جـارِ التحميل ▬▭ . . .🎧♥️╰**")

    try:
        api_url = "https://api-abztech.zone.id/download/ytmp3"

        response = await asyncio.to_thread(
            lambda: requests.get(
                api_url,
                params={"url": link},
                timeout=60
            )
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("status"):
            return await revent.edit(
                "**• فشل الـ API في تجهيز المقطع الصوتي ✖️**"
            )

        download = data.get("download") or {}
        audio_url = download.get("downloadUrl")

        if not audio_url:
            return await revent.edit(
                "**• لم يتم العثور على رابط تحميل الصوت ✖️**"
            )

        title = (download.get("title") or title)[:40]
        thumbnail = download.get("thumbnail")

        if thumbnail:
            try:
                thumb_response = await asyncio.to_thread(
                    lambda: requests.get(thumbnail, timeout=20)
                )
                thumb_response.raise_for_status()

                thumb_name = f"rep_thumb_{event.id}.jpg"
                with open(thumb_name, "wb") as f:
                    f.write(thumb_response.content)
            except Exception:
                thumb_name = None


        audio_file = f"rep_search_{event.id}.mp3"

        def download_audio():
            with requests.get(
                audio_url,
                stream=True,
                timeout=(20, 120)
            ) as audio_response:
                audio_response.raise_for_status()
                with open(audio_file, "wb") as f:
                    for chunk in audio_response.iter_content(
                        chunk_size=256 * 1024
                    ):
                        if chunk:
                            f.write(chunk)

        await asyncio.to_thread(download_audio)

        if not os.path.isfile(audio_file) or os.path.getsize(audio_file) == 0:
            return await revent.edit("**• ملف الصوت فارغ أو لم يكتمل تحميله ✖️**")

        duration_parts = duration_text.split(":")
        try:
            duration = 0
            for part in duration_parts:
                duration = duration * 60 + int(part)
        except (ValueError, TypeError):
            duration = 0

        await revent.edit("**╮ جـارِ الرفـع ▬▬ . . .🎧♥️╰**")

        await event.client.send_file(
            event.chat_id,
            audio_file,
            force_document=False,
            caption=f"**⎉ البحث ⥃** `{title}`",
            thumb=thumb_name,
            attributes=[
                DocumentAttributeAudio(
                    duration=duration,
                    title=title,
                    performer="Unknown"
                )
            ]
        )

        await revent.delete()

    except ChatSendMediaForbiddenError:
        await revent.edit("**- عـذراً .. الوسـائـط مغلقـه هنـا ؟!**")

    except Exception as e:
        await revent.edit(
            f"**• حدث خطأ أثناء التحميل:** `{str(e)}`"
        )

    finally:
        for file_path in (audio_file, thumb_name):
            try:
                if file_path and os.path.isfile(file_path):
                    os.remove(file_path)
            except OSError as e:
                print(f"Error cleaning up: {e}")
    
        
        
"""@zq_lo.rep_cmd(pattern="s(?: |$)(.*)")
async def _(event):
    query = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not query and reply:
        query = reply.text
    if not query:
        return await edit_or_reply(event, "**⎉╎قم باضافـة إسـم للامـر ..**\n**⎉╎بحث + اسـم المقطـع الصـوتي**")

    revent = await edit_or_reply(event, "**╮ جـارِ البحث ؏ـن المقطـٓع الصٓوتـي... 🎧♥️╰**")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await revent.edit("**• لم يتم العثور على نتائج للبحث.**")
        
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
    except Exception as e:
        return await revent.edit(f"**• فشـل في محرك البحث:** `{str(e)}`")

    await revent.edit(f"**╮ جـارِ تحميـل بحثك... 📥╰**\n**⎉ العنوان:** `{title[:30]}...`")
    
    assistant_bot = "@QJ9bot"
    async with event.client.conversation(assistant_bot, timeout=600) as conv:
        try:
            await conv.send_message(link)
            
            response = await conv.get_response()
            
            found_button = None
            if response.buttons:
                for row in response.buttons:
                    for button in row:
                        btn_text = button.text.lower()
                        if any(x in btn_text for x in ["ملف صوتي", "audio", "🎶", "تحميل", "download"]):
                            found_button = button
                            break
                    if found_button:
                        break
            
            if not found_button:
                await asyncio.sleep(2)
                messages = await event.client.get_messages(assistant_bot, limit=2)
                if messages and messages[0].buttons:
                    for row in messages[0].buttons:
                        for button in row:
                            btn_text = button.text.lower()
                            if any(x in btn_text for x in ["ملف صوتي", "Audio", "🎶", "تحميل", "download"]):
                                found_button = button
                                break
                        if found_button:
                            break
            
            if not found_button:
                return await revent.edit("**• لم أجد زر تحميل الصوت في رد البوت.**")
            
            await revent.edit("**╮ تم العثور على بحثك! جاري التحميل... 🎧╰**")
            await found_button.click()
            
            await asyncio.sleep(3)
            
            audio_msg = None
            max_attempts = 20
            
            for attempt in range(max_attempts):
                messages = await event.client.get_messages(assistant_bot, limit=5)
                
                for msg in messages:
                    if msg.media:
                        if hasattr(msg.media, 'document'):
                            mime_type = msg.media.document.mime_type
                            if mime_type.startswith('audio/'):
                                audio_msg = msg
                                break
                        elif hasattr(msg.media, 'audio'):
                            audio_msg = msg
                            break
                        elif hasattr(msg.media, 'photo'):
                            continue
                
                if audio_msg:
                    break
                
                await revent.edit(f"**╮ جاري البحث عن الملف الصوتي... ({attempt+1}/{max_attempts}) ⏳╰**")
                await asyncio.sleep(2)
            
            if audio_msg and audio_msg.media:
                await revent.edit("**╮ جـارِ الرفـع ▬▬ . . .🎧♥️╰**")
                await event.client.send_file(
                    event.chat_id,
                    audio_msg.media,
                    caption=f"**⎉ البحث ⥃** `{title}`",
                    reply_to=reply.id if reply else None
                )
                await revent.delete()
            else:
                await revent.edit("**• لم يتم العثور على ملف صوتي في ردود البوت.**")

        except asyncio.TimeoutError:
            await revent.edit("**• انتهت مهلة الانتظار للبوت.**")
        except Exception as e:
            await revent.edit(f"**• خطأ في المحادثة:** `{str(e)}`")"""

#R
@zq_lo.rep_cmd(pattern="فيديو(?: |$)(.*)")
async def _(event):
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
    elif reply and reply.message:
        query = reply.message
    else:
        return await edit_or_reply(
            event,
            "**⎉╎قم باضافـة إسـم للامـر ..**\n"
            "**⎉╎فيديو + اسـم الفيديـو.**"
        )

    revent = await edit_or_reply(
        event,
        "**╮ جـارِ البحث ؏ـن الفيديـو... 🎧♥️╰**"
    )

    file_name = None
    thumb_name = None

    try:
        results = await asyncio.to_thread(
            lambda: YoutubeSearch(query, max_results=1).to_dict()
        )

        if not results:
            return await revent.edit(
                "**• لم يتم العثور على أي نتيجة ✖️**"
            )

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0].get("title", "Video")[:40]

    except Exception as e:
        return await revent.edit(
            f"**• فشـل في البحث**\n**• الخطـأ :** `{str(e)}`"
        )

    try:
        await revent.edit("**╮ جـارِ التحميل ▬▭ . . .🎧♥️╰**")

        api_url = "https://api-abztech.zone.id/download/omdown"

        response = await asyncio.to_thread(
            lambda: requests.get(
                api_url,
                params={"url": link},
                timeout=60
            )
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            return await revent.edit(
                "**• فشل الـ API في جلب الفيديو ✖️**"
            )

        formats = data.get("formats") or []

        video_formats = []

        for fmt in formats:
            if (
                fmt.get("kind") == "video"
                and fmt.get("ext", "").lower() == "mp4"
                and fmt.get("url")
            ):
                match = re.search(
                    r"(\d+)\s*p",
                    fmt.get("label", ""),
                    re.IGNORECASE
                )

                if match:
                    quality = int(match.group(1))
                    video_formats.append((quality, fmt["url"]))

        if not video_formats:
            return await revent.edit(
                "**• لم يتم العثور على صيغة فيديو MP4 متاحة ✖️**"
            )

        video_formats.sort(key=lambda item: item[0], reverse=True)
        quality, video_url = video_formats[0]
        title = (data.get("title") or title)[:40]
        thumbnail = data.get("cover")

        if thumbnail:
            try:
                thumb_response = await asyncio.to_thread(
                    lambda: requests.get(thumbnail, timeout=20)
                )
                thumb_response.raise_for_status()

                thumb_name = f"rep_video_thumb_{event.id}.jpg"

                with open(thumb_name, "wb") as f:
                    f.write(thumb_response.content)

            except Exception:
                thumb_name = None

        file_name = f"rep_video_{event.id}.mp4"

        def download_video():
            with requests.get(
                video_url,
                stream=True,
                timeout=(20, 180)
            ) as video_response:
                video_response.raise_for_status()

                with open(file_name, "wb") as f:
                    for chunk in video_response.iter_content(
                        chunk_size=256 * 1024
                    ):
                        if chunk:
                            f.write(chunk)

        await asyncio.to_thread(download_video)

        if (
            not os.path.isfile(file_name)
            or os.path.getsize(file_name) == 0
        ):
            return await revent.edit(
                "**• فشل تحميل الفيديو أو أن الملف فارغ ✖️**"
            )

        await revent.edit("**╮ جـارِ الرفـع ▬▬ . . .🎧♥️╰**")

        await event.client.send_file(
            event.chat_id,
            file_name,
            caption=f"**⎉ البحث ⥃** `{title}`",
            thumb=thumb_name,
            supports_streaming=True,
            attributes=[
                DocumentAttributeVideo(
                    duration=0,
                    w=0,
                    h=0,
                    supports_streaming=True
                )
            ]
        )

        await revent.delete()

    except ChatSendMediaForbiddenError:
        await revent.edit(
            "**- عـذرًا .. الوسـائـط مغلقـه هنـا ؟!**"
        )

    except Exception as e:
        await revent.edit(
            f"**• فشـل التحميـل**\n"
            f"**• الخطـأ :** `{str(e)}`\n\n"
            "**• قم بإرسال هذا الخلل لمطور السورس لإصلاحه**\n"
            "**• تواصل مطور السورس @RR0RT**"
        )

    finally:
        for path in (file_name, thumb_name):
            try:
                if path and os.path.isfile(path):
                    os.remove(path)
            except OSError as e:
                print(f"Error cleaning up: {e}")


# ================================================================================================ #
# =========================================ردود الخاص================================================= #
# ================================================================================================ #

@zq_lo.rep_cmd(
    pattern="ابحث(?:\ع|$)([\\s\\S]*)",
    command=("ابحث", plugin_category),
    info={
        "header": "To reverse search song.",
        "الوصـف": "Reverse search audio file using shazam api",
        "امـر مضـاف": {"ع": "To send the song of sazam match"},
        "الاستخـدام": [
            "{tr}ابحث بالــرد ع بصمـه او مقطـع صوتي",
            "{tr}ابحث ع بالــرد ع بصمـه او مقطـع صوتي",
        ],
    },
)
async def shazamcmd(event):
    "To reverse search song."
    reply = await event.get_reply_message()
    mediatype = await media_type(reply)
    chat = "@DeezerMusicBot"
    delete = False
    flag = event.pattern_match.group(1)
    if not reply or not mediatype or mediatype not in ["Voice", "Audio"]:
        return await edit_delete(
            event, "**- بالــرد ع مقطـع صـوتي**"
        )
    revent = await edit_or_reply(event, "**- جـار تحميـل المقـطع الصـوتي ...**")
    name = "repthon.mp3"
    try:
        for attr in getattr(reply.document, "attributes", []):
            if isinstance(attr, types.DocumentAttributeFilename):
                name = attr.file_name
        dl = io.FileIO(name, "a")
        await event.client.fast_download_file(
            location=reply.document,
            out=dl,
        )
        dl.close()
        mp3_fileto_recognize = open(name, "rb").read()
        shazam = Shazam(mp3_fileto_recognize)
        recognize_generator = shazam.recognizeSong()
        track = next(recognize_generator)[1]["track"]
    except Exception as e:
        LOGS.error(e)
        return await edit_delete(
            revent, f"**- خطـأ :**\n__{e}__"
        )

    file = track["images"]["background"]
    title = track["share"]["subject"]
    slink = await yt_search(title)
    if flag == "s":
        deezer = track["hub"]["providers"][1]["actions"][0]["uri"][15:]
        async with event.client.conversation(chat) as conv:
            try:
                purgeflag = await conv.send_message("/start")
            except YouBlockedUserError:
                await zq_lo(unblock("DeezerMusicBot"))
                purgeflag = await conv.send_message("/start")
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.send_message(deezer)
            await event.client.get_messages(chat)
            song = await event.client.get_messages(chat)
            await song[0].click(0)
            await conv.get_response()
            file = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            delete = True
    await event.client.send_file(
        event.chat_id,
        file,
        caption=f"<b>⎉╎ المقطـع الصـوتي :</b> <code>{title}</code>\n<b>⎉╎ الرابـط : <a href = {slink}/1>YouTube</a></b>",
        reply_to=reply,
        parse_mode="html",
    )
    await revent.delete()
    if delete:
        await delete_conv(event, chat, purgeflag)


# Code R
@zq_lo.rep_cmd(pattern=".ff(?:\\s|$)([\\s\\S]*)")
async def song(event):
    song = event.pattern_match.group(1)
    chat = "@ROOTMusic_bot"
    reply_id_ = await reply_id(event)
    revent = await edit_or_reply(event, SONG_SEARCH_STRING, parse_mode="html")
    async with event.client.conversation(chat) as conv:
        try:
            purgeflag = await conv.send_message("/start")
        except YouBlockedUserError:
            await zq_lo(unblock("ROOTMusic_bot"))
            await conv.send_message("/start")
        await conv.send_message(song)
        hmm = await conv.get_response()
        rrr = await event.client.get_messages(chat)
        await revent.edit(SONG_SENDING_STRING, parse_mode="html")
        await rrr[0].click(0)
        await conv.get_response()
        music = await conv.get_response()
        await event.client.send_read_acknowledge(conv.chat_id)
        await event.client.send_file(
            event.chat_id,
            music,
            caption=f"<b>⎉ البحث ⥃ <code>{song}</code></b>",
            parse_mode="html",
            reply_to=reply_id_,
        )
        await revent.delete()
        await delete_conv(event, chat, purgeflag)


@zq_lo.rep_cmd(
    pattern="يوتيوب(?: |$)(\\d*)? ?([\\s\\S]*)",
    command=("يوتيوب", plugin_category),
    info={
        "header": "لـ البحـث عـن روابــط بالكلمــه المحــدده علـى يـوتيــوب",
        "مثــال": [
            "{tr}يوتيوب + كلمـه",
            "{tr}يوتيوب + عدد + كلمـه",
        ],
    },
)
async def you_search(event):
    "Youtube search command"
    if event.is_reply and not event.pattern_match.group(2):
        query = await event.get_reply_message()
        query = str(query.message)
    else:
        query = str(event.pattern_match.group(2))
    if not query:
        return await edit_delete(
            event, "**╮ بالـرد ﮼؏ كلمـٓھہ للبحث أو ضعها مـع الأمـر ... 𓅫╰**"
        )
    video_q = await edit_or_reply(event, "**╮ جـارِ البحث ▬▭... ╰**")
    if event.pattern_match.group(1) != "":
        lim = int(event.pattern_match.group(1))
        if lim <= 0:
            lim = int(10)
    else:
        lim = int(10)
    try:
        full_response = await ytsearch(query, limit=lim)
    except Exception as e:
        return await edit_delete(video_q, str(e), time=10, parse_mode=_format.parse_pre)
    reply_text = f"**•  اليك عزيزي قائمة بروابط الكلمة اللتي بحثت عنها:**\n`{query}`\n\n**•  النتائج:**\n{full_response}"
    await edit_or_reply(video_q, reply_text)


async def ytdl_down(event, opts, url):
    ytdl_data = None
    try:
        await event.edit("**╮ ❐ يتـم جلـب البيانـات انتظـر قليلاً ...𓅫╰▬▭ **")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await event.edit(f"`{DE}`")
    except ContentTooShortError:
        await event.edit("**- عذرا هذا المحتوى قصير جدا لتنزيله ⚠️**")
    except GeoRestrictedError:
        await event.edit(
            "**- الفيديو غير متاح من موقعك الجغرافي بسبب القيود الجغرافية التي يفرضها موقع الويب ❕**"
        )
    except MaxDownloadsReached:
        await event.edit("**- تم الوصول إلى الحد الأقصى لعدد التنزيلات ❕**")
    except PostProcessingError:
        await event.edit("**كان هناك خطأ أثناء المعالجة**")
    except UnavailableVideoError:
        await event.edit("**⌔∮عـذرًا .. الوسائط غير متوفـره بالتنسيق المطلـوب**")
    except XAttrMetadataError as XAME:
        await event.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    except ExtractorError:
        await event.edit("**حدث خطأ أثناء استخراج المعلومات يرجى وضعها بشكل صحيح ⚠️**")
    except Exception as e:
        await event.edit(f"**Error : **\n__{e}__")
    return ytdl_data


async def fix_attributes(
    path, info_dict: dict, supports_streaming: bool = False, round_message: bool = False
) -> list:
    """Avoid multiple instances of an attribute."""
    new_attributes = []
    video = False
    audio = False

    uploader = info_dict.get("uploader", "Unknown artist")
    duration = int(info_dict.get("duration", 0))
    suffix = path.suffix[1:]
    if supports_streaming and suffix != "mp4":
        supports_streaming = True

    attributes, mime_type = get_attributes(path)
    if suffix == "mp3":
        title = str(info_dict.get("title", info_dict.get("id", "Unknown title")))
        audio = types.DocumentAttributeAudio(
            duration=duration, voice=None, title=title, performer=uploader
        )
    elif suffix == "mp4":
        width = int(info_dict.get("width", 0))
        height = int(info_dict.get("height", 0))
        for attr in attributes:
            if isinstance(attr, types.DocumentAttributeVideo):
                duration = duration or attr.duration
                width = width or attr.w
                height = height or attr.h
                break
        video = types.DocumentAttributeVideo(
            duration=duration,
            w=width,
            h=height,
            round_message=round_message,
            supports_streaming=supports_streaming,
        )

    if audio and isinstance(audio, types.DocumentAttributeAudio):
        new_attributes.append(audio)
    if video and isinstance(video, types.DocumentAttributeVideo):
        new_attributes.append(video)

    new_attributes.extend(
        attr
        for attr in attributes
        if (
            isinstance(attr, types.DocumentAttributeAudio)
            and not audio
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not video
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not isinstance(attr, types.DocumentAttributeVideo)
        )
    )
    return new_attributes, mime_type


@zq_lo.rep_cmd(
    pattern="تحميل صوت(?: |$)(.*)",
    command=("تحميل صوت", plugin_category),
    info={
        "header": "تحميـل الاغـاني مـن يوتيوب .. فيسبوك .. انستا .. الـخ عـبر الرابـط",
        "مثــال": ["{tr}تحميل صوت بالــرد ع رابــط", "{tr}تحميل صوت + رابــط"],
    },
)
async def download_audio(event):
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    revent = await edit_or_reply(event, "**⌔╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        try:
            vid_data = YoutubeDL({"no-playlist": True, "cookiefile": get_cookies_file()}).extract_info(
                url, download=False
            )
        except ExtractorError:
            vid_data = {"title": url, "uploader": "Catuserbot", "formats": []}
        startTime = time()
        retcode = await _mp3Dl(url=url, starttime=startTime, uid="320")
        if retcode != 0:
            return await event.edit(str(retcode))
        _fpath = ""
        thumb_pic = None
        for _path in glob.glob(os.path.join(Config.TEMP_DIR, str(startTime), "*")):
            if _path.lower().endswith((".jpg", ".png", ".webp")):
                thumb_pic = _path
            else:
                _fpath = _path
        if not _fpath:
            return await edit_delete(revent, "__Unable to upload file__")
        await revent.edit(
            f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
            \n**{vid_data['title']}***"
        )
        attributes, mime_type = get_attributes(str(_fpath))
        ul = io.open(pathlib.Path(_fpath), "rb")
        if thumb_pic is None:
            thumb_pic = str(
                await pool.run_in_thread(download)(
                    await get_ytthumb(get_yt_video_id(url))
                )
            )
        uploaded = await event.client.fast_upload_file(
            file=ul,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    revent,
                    startTime,
                    "trying to upload",
                    file_name=os.path.basename(pathlib.Path(_fpath)),
                )
            ),
        )
        ul.close()
        media = types.InputMediaUploadedDocument(
            file=uploaded,
            mime_type=mime_type,
            attributes=attributes,
            force_file=False,
            thumb=await event.client.upload_file(thumb_pic) if thumb_pic else None,
        )
        try:
            await event.client.send_file(
                event.chat_id,
                file=media,
                caption=f"<b>⎉ تحميـل ⥃ </b><code>{vid_data.get('title', os.path.basename(pathlib.Path(_fpath)))}</code>",
                supports_streaming=True,
                reply_to=reply_to_id,
                parse_mode="html",
            )
        except ChatSendMediaForbiddenError: # b
            return await revent.edit("**- عـذرًا .. الوسـائـط مغلقـه هنـا ؟!**")
        except Exception as e: # b
            return await revent.edit(f"**• فشـل التحميـل** \n**• الخطـأ :** `{str(e)}`\n\n**• غالباً .. التحميل غير متاح في هذه الدردشـة ✖️**")
        for _path in [_fpath, thumb_pic]:
            os.remove(_path)
    await revent.delete()

@zq_lo.rep_cmd(
    pattern="تحميل فيديو(?: |$)(.*)",
    command=("تحميل فيديو", plugin_category),
    info={
        "header": "تحميـل مقـاطـع الفيـديــو مـن يوتيوب .. فيسبوك .. انستا .. الـخ عـبر الرابـط",
        "مثــال": [
            "{tr}تحميل فيديو بالــرد ع رابــط",
            "{tr}تحميل فيديو + رابــط",
        ],
    },
)
async def download_video(event):
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    revent = await edit_or_reply(event, "**⌔╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    for url in urls:
        ytdl_data = await ytdl_down(revent, video_opts, url)
        if ytdl_data is None:
            return
        try:
            f = pathlib.Path("rep_ytv.mp4")
            print(f)
            rthumb = pathlib.Path("rep_ytv.jpg")
            if not os.path.exists(rthumb):
                rthumb = pathlib.Path("rep_ytv.webp")
            if not os.path.exists(rthumb):
                rthumb = None
            await revent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{ytdl_data['title']}**"
            )
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                f, ytdl_data, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, revent, c_time, "Upload :", file_name=ytdl_data["title"]
                    )
                ),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            try:
                await event.client.send_file(
                    event.chat_id,
                    file=media,
                    reply_to=reply_to_id,
                    caption=f'**⎉ تحميـل ⥃** `{ytdl_data["title"]}`',
                    thumb=rthumb,
                )
            except ChatSendMediaForbiddenError: # R
                return await revent.edit("**- عـذرًا .. الوسـائـط مغلقـه هنـا ؟!**")
            except Exception as e: # R
                return await revent.edit(f"**• فشـل التحميـل** \n**• الخطـأ :** `{str(e)}`\n\n**• غالباً .. التحميل غير متاح في هذه الدردشـة ✖️**")
            os.remove(f)
            if rthumb:
                os.remove(rthumb)
        except TypeError:
            await asyncio.sleep(2)
    await revent.delete()
