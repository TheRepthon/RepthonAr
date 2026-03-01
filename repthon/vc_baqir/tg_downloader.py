import asyncio
import os
import pathlib
import time
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from ..core.managers import edit_or_reply
from ..Config import Config
from ..helpers import progress


BASE_DIR = pathlib.Path(os.getcwd())
DOWNLOADS = BASE_DIR / "temp"
DOWNLOADS.mkdir(parents=True, exist_ok=True)


async def tg_dl(event):
    msg = await edit_or_reply(event, "**- جاري التحميل من تيليجرام 📥...**")

    reply = await event.get_reply_message()

    if not reply or not reply.media:
        await msg.edit("**- يجب الرد على ملف صوتي او فيديو ❌**")
        return False

    if not reply.document:
        await msg.edit("**- هذا ليس ملف قابل للتشغيل ❌**")
        return False

    is_audio = any(
        isinstance(attr, DocumentAttributeAudio)
        for attr in reply.document.attributes
    )

    is_video = any(
        isinstance(attr, DocumentAttributeVideo)
        for attr in reply.document.attributes
    )

    if not (is_audio or is_video):
        await msg.edit("**- الملف يجب أن يكون صوت او فيديو فقط ❌**")
        return False

    file_name = getattr(reply.document, "file_name", None)
    if not file_name:
        file_name = f"repthon_{reply.id}.mp4" if is_video else f"repthon_{reply.id}.mp3"

    file_name = os.path.basename(file_name)
    file_path = DOWNLOADS / file_name

    start = time.time()

    try:
        downloaded_file = await event.client.download_media(
            reply,
            file=str(file_path),
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, msg, start, "**- جاري التحميل 📥...**")
            ),
        )
    except Exception as e:
        await msg.edit(f"**- حدث خطأ أثناء التحميل ❌:**\n`{str(e)}`")
        return False

    if not downloaded_file or not os.path.exists(downloaded_file):
        await msg.edit("**- فشل التحميل ❌**")
        return False

    elapsed = int(time.time() - start)

    await msg.edit(
        f"**❈╎تم التحميل بنجاح ✅**\n"
        f"**❈╎الوقت المستغرق: {elapsed} ثانية**\n"
        f"**❈╎المسار:** `{downloaded_file}`"
    )

    return str(downloaded_file)
