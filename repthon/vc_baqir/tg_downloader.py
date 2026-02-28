import asyncio
import os
import pathlib
import time
from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers import progress

downloads = pathlib.Path(os.path.join(os.getcwd(), "temp"))
downloads.mkdir(parents=True, exist_ok=True)

async def tg_dl(event):
    mone = await edit_or_reply(event, "**- جاري التحميل من تيليجرام 📥...**")
    reply = await event.get_reply_message()
    
    if not reply or not reply.media:
        await mone.edit("**- عذراً، يجب الرد على فيديو أو ملف صوتي...**")
        return False

    file_name = getattr(reply.document, "file_name", None) or f"repthon_{reply.id}"
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

    await mone.edit(
        f"**❈╎تم التحميل بنجاح ✅**\n"
        f"**❈╎الوقت المستغرق: {elapsed} ثانية.**\n"
        f"**❈╎المسار:** `{downloaded_file}`"
    )
    
    return str(downloaded_file)
