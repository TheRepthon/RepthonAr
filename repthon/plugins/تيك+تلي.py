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
        "**⎉╎جارِ تحميل من التيك توك... انتظر قليلاً ⏳**"
    )

    try:
        async with borg.conversation(chat, timeout=120) as conv:
            await conv.send_message(link)

            
            media_list = []
            seen_ids = set()

            for _ in range(10):
                try:
                    response = await conv.get_response()
                except Exception:
                    break

                if not response or not response.media:
                    continue

                if response.audio:
                    continue

                if response.document:
                    mime = getattr(
                        response.document,
                        "mime_type",
                        ""
                    ) or ""

                    if mime.startswith("audio/"):
                        continue

                    if not (
                        mime.startswith("image/")
                        or mime.startswith("video/")
                    ):
                        continue

                if response.id in seen_ids:
                    continue
                seen_ids.add(response.id)
                media_list.append(response)
            if not media_list:
                await rep.edit(
                    "**- لم أجد صوراً أو فيديوهات في ردود البوت.**"
                )
                return
            caption = (
                "<b>⎉╎تم التحميل بنجاح ☑️\n"
                "⎉╎بواسطة "
                "<a href='https://t.me/Repthon'>Repthon</a></b>"
            )
            
            for index, item in enumerate(media_list):
                await borg.send_file(
                    event.chat_id,
                    item.media,
                    caption=caption if index == 0 else None,
                    parse_mode="html" if index == 0 else None,
                    reply_to=event.reply_to_msg_id
                )

            await rep.delete()

    except Exception as e:
        await rep.edit(
            f"**- حدث خطأ أثناء التحميل:**\n`{str(e)[:500]}`"
        )


# Write Code By telegram.dog/E_7_V ✌🏻
@zq_lo.rep_cmd(pattern=f"ستوري(?: |$)(.*)")
async def baqir(event):
    TIBA = event.pattern_match.group(1)
    baq = None
    if TIBA:
        baqir = TIBA
        baq = baqir
    elif event.is_reply:
        baqir = await event.get_reply_message()
        baq = baqir.message
    else:
        return await edit_or_reply(event, "**⎉╎باضافة رابـط ستـوري لـ الامـر او بالـࢪد ؏ــلى رابـط الستـوري**")
    if not baq:
        return await edit_or_reply(event, "**⎉╎باضافة رابـط ستـوري لـ الامـر او بالـࢪد ؏ــلى رابـط الستـوري**")
    if ("https://t.me" not in baq) and ("/s/" not in baq):
        return await edit_delete(event, "**- قم بإدخـال رابـط ستـوري صالـح .. للتحميــل ❌**", 10)
    #chat_url = "https://t.me/msaver_bot?start=1895219306"
    rrr = await edit_or_reply(event, f"**- جـارِ تحميـل الستـوري انتظـر ... 🍧╰\n- رابـط الستـوري :\n{baq}**")
    chat = "@msaver_bot"
    async with borg.conversation(chat) as conv:
        try:
            purgeflag = await conv.send_message(baqir)
        except YouBlockedUserError:
            await zq_lo(unblock("msaver_bot"))
            purgeflag = await conv.send_message(baqir)
        response = await conv.get_response()
        await asyncio.sleep(3)
        if response.media:
            repthon = response.media
        else:
            repthon = await conv.get_response()
        await borg.send_file(
            event.chat_id,
            repthon,
            caption=f"<b>⎉╎تم تحميـل ستـوري تيليجرام .. بنجـاح 🎆\n⎉╎الرابـط 🖇:  {baq}\n⎉╎تم التحميـل بواسطـة <a href = https://t.me/Repthon>𝗥𝗲𝗽𝘁𝗵𝗼𝗻</a> </b>",
            parse_mode="html",
        )
        await rrr.delete()
        await delete_conv(event, chat, purgeflag)
        await event.client(DeleteHistoryRequest(6135950112, max_id=0, just_clear=True))
