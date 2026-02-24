import asyncio
import os
import pathlib
import time
from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers import progress

downloads = pathlib.Path(os.path.join(os.getcwd(), Config.TMP_DOWNLOAD_DIRECTORY))
downloads.mkdir(parents=True, exist_ok=True)

async def tg_dl(event):
    mone = await edit_or_reply(event, "**- جاري التحميل من تيليجرام 📥...**")
    reply = await event.get_reply_message()
    
    if not reply or not reply.media:
        await mone.edit("**- عذراً، يجب الرد على فيديو أو ملف صوتي...**")
        return False

    file_name = getattr(reply.document, "file_name", None) or f"repthon_{reply.id}.mp3"
    file_path = downloads / file_name
    
    start = time.time()
    
    try:
        downloaded_file = await event.client.download_media(
            reply,
            file=str(file_path),
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, mone, start, "**- جاري التحميل 📥...**")
            ),
        )
    except Exception as e:
        await mone.edit(f"**- حدث خطأ أثناء التحميل:**\n`{str(e)}`")
        return False

    elapsed = int(time.time() - start)
    
    rel_path = os.path.relpath(downloaded_file, os.getcwd())
    
    await mone.edit(
        f"**❈╎تم التحميل بنجاح ✅**\n"
        f"**❈╎الوقت المستغرق: {elapsed} ثانية.**\n"
        f"**❈╎المسار:** `{rel_path}`"
    )
    
    return rel_path
