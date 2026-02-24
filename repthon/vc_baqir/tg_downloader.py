import asyncio
import io
import os
import pathlib
import time
from datetime import datetime
from telethon.tl import types
from telethon.utils import get_extension
from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers import progress

downloads = pathlib.Path(os.path.join(os.getcwd(), Config.TMP_DOWNLOAD_DIRECTORY))
downloads.mkdir(parents=True, exist_ok=True)


async def tg_dl(event):
    mone = await edit_or_reply(event, "**- جاري التحميل 📥...**")
    reply = await event.get_reply_message()
    if not reply:
        await mone.edit("**- بالرد على فيديو أو ملف صوتي لتشغيله...**")
        return False

    name = getattr(reply.document, "file_name", None) or f"untitled_{reply.id}"
    ext = get_extension(reply.document) if getattr(reply, "document", None) else ""
    file_path = downloads / name
    if not file_path.suffix and ext:
        file_path = file_path.with_suffix(ext)

    file_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.time()
    if getattr(reply, "document", None):
        async with io.FileIO(file_path, "wb") as f:
            await event.client.fast_download_file(
                location=reply.document,
                out=f,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, start, "**- جاري التحميل 📥...**")
                ),
            )
    else:
        file_path = await reply.download_media(
            file=file_path,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, mone, start, "**- جاري التحميل 📥...**")
            ),
        )

    elapsed = int(time.time() - start)
    await mone.edit(
        f"**❈╎تم التحميل خلال {elapsed} ثانية.**\n"
        f"**❈╎مسار التحميل: ** `{os.path.relpath(file_path, os.getcwd())}`"
    )
    return os.path.relpath(file_path, os.getcwd())
