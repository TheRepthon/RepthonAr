import asyncio

from telethon.errors.rpcerrorlist import YouBlockedUserError, ChatSendMediaForbiddenError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.tl.functions.contacts import BlockRequest as bloock

from repthon import zq_lo

from ..core.managers import edit_delete, edit_or_reply
from ..helpers import get_user_from_event, sanga_seperator
from ..helpers.utils import _format

plugin_category = "العروض"


@zq_lo.rep_cmd(pattern="كشف(?: |$)(.*)")
async def get_about(event):
    input_str = event.pattern_match.group(1)
    reply_message = await event.get_reply_message()
    if not input_str and not reply_message:
        await edit_or_reply(event, "**- بالـرد ع الشخص او باضافة معـرف/ايـدي الشخـص للامـر**")
    if input_str and not reply_message:
        if input_str.isnumeric():
            uid = input_str
        if input_str.startswith("@"):
            user = await event.client.get_entity(input_str)
            uid = user.id
    if input_str and reply_message:
        if input_str.isnumeric():
            uid = input_str
        if input_str.startswith("@"):
            user = await event.client.get_entity(input_str)
            uid = user.id
    if not input_str and reply_message:
        user = await event.client.get_entity(reply_message.sender_id)
        uid = user.id
    #user = await get_user_from_event(event)
    #if not user:
        #return
    #uid = user.id
    chat = "@SangMata_beta_bot" 
    rep = await edit_or_reply(event, "**⎉╎جـارِ الكشـف ...**")
    async with borg.conversation(chat) as conv: 
        try:
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(f"{uid}")
        except YouBlockedUserError:
            await zq_lo(unblock("SangMata_beta_bot"))
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(f"{uid}")
        rrr = await conv.get_response()
        malak = rrr.text
        if "No data available" in malak: 
            rr = "<b>⎉╎المستخدم ليس لديه أي سجل اسمـاء بعـد ...</b>"
            await rep.delete()
            return await borg.send_message(event.chat_id, rr, parse_mode="html")
        if "Sorry, you have used up your quota for today" in rrr.text:
            rr = "<b>⎉╎عـذراً .. لقد استنفدت محاولاتك لهذا اليوم.\n⎉╎لديـك 5 محاولات فقط كل يوم\n⎉╎يتم تحديث محاولاتك في الساعة 03:00 بتوقيت مكة كل يوم</b>"
            await rep.delete()
            return await borg.send_message(event.chat_id, rrr, parse_mode="html")
        if "👤 History for" in malak:
            rr = malak.replace("👤 History for", "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 - <b>سجـل الحسـاب 🪪\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n⌔ تم جلب السجـلات .. بنجـاح ☑️</b> ❝") 
            await rep.delete()
            return await borg.send_message(event.chat_id, rr, parse_mode="html")
        await rep.delete()
        return await borg.send_message(event.chat_id, rrr, parse_mode="html")


@zq_lo.rep_cmd(pattern="الاسماء(?: |$)(.*)")
async def get_about(event):
    input_str = event.pattern_match.group(1)
    reply_message = await event.get_reply_message()
    if not input_str and not reply_message:
        await edit_or_reply(event, "**- بالـرد ع الشخص او باضافة معـرف/ايـدي الشخـص للامـر**")
    if input_str and not reply_message:
        if input_str.isnumeric():
            uid = input_str
        if input_str.startswith("@"):
            user = await event.client.get_entity(input_str)
            uid = user.id
    if input_str and reply_message:
        if input_str.isnumeric():
            uid = input_str
        if input_str.startswith("@"):
            user = await event.client.get_entity(input_str)
            uid = user.id
    if not input_str and reply_message:
        user = await event.client.get_entity(reply_message.sender_id)
        uid = user.id
    #user = await get_user_from_event(event)
    #if not user:
        #return
    #uid = user.id
    chat = "@SangMata_beta_bot" 
    rep = await edit_or_reply(event, "**⎉╎جـارِ الكشـف ...**")
    async with borg.conversation(chat) as conv: 
        try:
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(f"{uid}")
        except YouBlockedUserError:
            await zq_lo(unblock("SangMata_beta_bot"))
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(f"{uid}")
        ba = await conv.get_response()
        malak = ba.text
        if "No data available" in malak: 
            baqir = "<b>⎉╎المستخدم ليس لديه أي سجل اسمـاء بعـد ...</b>"
            await rep.delete()
            return await borg.send_message(event.chat_id, baqir, parse_mode="html")
        if "Sorry, you have used up your quota for today" in ba.text:
            baqir = "<b>⎉╎عـذراً .. لقد استنفدت محاولاتك لهذا اليوم.\n⎉╎لديـك 5 محاولات فقط كل يوم\n⎉╎يتم تحديث محاولاتك في الساعة 03:00 بتوقيت مكة كل يوم</b>"
            await rep.delete()
            return await borg.send_message(event.chat_id, baqir, parse_mode="html")
        if "👤 History for" in malak:
            baqir = malak.replace("👤 History for", "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 - <b>سجـل الحسـاب 🪪\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n⌔ تم جلب السجـلات .. بنجـاح ☑️</b> ❝") 
            await rep.delete()
            return await borg.send_message(event.chat_id, baqir, parse_mode="html")
        await rep.delete()
        return await borg.send_message(event.chat_id, ba, parse_mode="html")
