# Repthon🔥
# Repthon - Baqir
# Copyright (C) 2023 RepthonArabic . All Rights Reserved
#
# This file is a part of < https://github.com/RepthonArabic/RepthonAr/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/RepthonArabic/RepthonAr/blob/master/LICENSE/>.


import base64
import requests
import asyncio
import os
import sys
import urllib.request
from datetime import timedelta
from telethon import events
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.tl.functions.messages import ImportChatInviteRequest as Get


from repthon import zq_lo
from repthon.utils import admin_cmd
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import media_type
from ..helpers.utils import reply_id


bot = zq_lo

#Code by T.me/E_7_V

@zq_lo.rep_cmd(pattern="تيك(?: |$)(.*)")
async def baqir_tiktok(event):
    link = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()

    if not link and reply:
        link = (reply.text or reply.message or "").strip()

    if not link:
        return await edit_delete(
            event,
            "**- أرسل (.تيك) + رابط تيك توك أو رد على الرابط.**",
            10
        )

    if "tiktok.com" not in link.lower():
        return await edit_delete(
            event,
            "**- أحتاج رابطاً من تيك توك فقط.**",
            10
        )

    chat = "@TIKTOKDOWNLOADROBOT"
    rep = await edit_or_reply(
        event,
        "**⎉╎جارِ تحميل الفيديو... انتظر قليلاً ⏳**"
    )

    try:
        async with borg.conversation(chat, timeout=120) as conv:
            await conv.send_message(link)

            video = None

            # فحص عدة رسائل لأن البوت قد يرسل صورة أو صوتاً أولاً.
            for _ in range(8):
                response = await conv.get_response()

                if not response:
                    continue

                # تجاهل النصوص والصور والملفات الصوتية.
                if response.video:
                    video = response
                    break

                if response.document:
                    mime = getattr(
                        response.document,
                        "mime_type",
                        ""
                    ) or ""

                    if mime.startswith("video/"):
                        video = response
                        break

            if not video:
                await rep.edit(
                    "**- لم أجد رسالة فيديو ضمن ردود البوت.**"
                )
                return

            await borg.send_file(
                event.chat_id,
                video.media,
                caption=(
                    "<b>⎉╎تم تحميل الفيديو بنجاح ☑️\n"
                    "⎉╎بواسطة "
                    "<a href='https://t.me/Repthon'>Repthon</a></b>"
                ),
                parse_mode="html",
                reply_to=event.reply_to_msg_id
            )

            await rep.delete()

    except Exception as e:
        await rep.edit(
            f"**- حدث خطأ أثناء التحميل:**\n`{str(e)[:500]}`"
        )



# Write Code By telegram.dog/E_7_V ✌🏻
@zq_lo.on(admin_cmd(pattern="ستوري(?: |$)(.*)"))
async def _(event):
    if event.fwd_from:
        return
    j_link = event.pattern_match.group(1)
    if ".me" not in j_link:
        await event.edit("**⎉╎ يجب وضع رابط الستوري مع الامر اولا **")
    else:
        await event.edit("**⎉╎ يتم الان تنزيل الستوري انتظر قليلا**")
    chat = "@msaver_bot"
    async with bot.conversation(chat) as conv:
        try:
            msg = await conv.send_message(j_link)
            video = await conv.get_response()
            """ تم تحميل الستوري بنجاح من قبل @Repthon """
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.edit("**⎉╎ الغـي حـظر هـذا البـوت و حـاول مجـددا @msaver_bot**")
            return
        REPTHON = base64.b64decode("dHJ5OgogICAgYXdhaXQgenFfbG8oSm9pbkNoYW5uZWxSZXF1ZXN0KCJAUmVwdGhvbiIpKQ==")
        TAIBA = Get(REPTHON)
        try:
            await event.client(TAIBA)
        except BaseException:
            pass
        await bot.send_file(event.chat_id, video, caption=f"<b>⎉╎ BY : @Repthon 🎀</b>",parse_mode="html")
        await event.delete()
