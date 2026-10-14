import re
import datetime
from asyncio import sleep

from telethon import events
from telethon.utils import get_display_name

from . import zq_lo
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import pmpermit_sql as pmpermit_sql
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.pasmat_sql import (
    add_pasmat,
    get_pasmats,
    remove_all_pasmats,
    remove_pasmat,
)
from ..sql_helper.pmrad_sql import (
    add_pmrad,
    get_pmrads,
    remove_all_pmrads,
    remove_pmrad,
)
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "الخدمات"
LOGS = logging.getLogger(__name__)


BaqirMeMe_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 - اوامـر البصمـات 🎙](t.me/Repthon) 𓆪\n\n"
    "**✾╎قائـمه اوامـر ردود البصمات والميديا العامـه🎙:**\n\n"
    "**⎞𝟏⎝** `.بصمه`\n"
    "**•• ⦇الامـر + كلمـة الـرد بالـرد ع بصمـه او ميديـا⦈ لـ اضـافة رد بصمـه عـام**\n\n"
    "**⎞𝟐⎝** `.حذف بصمه`\n"
    "**•• ⦇الامـر + كلمـة البصمـه⦈ لـ حـذف رد بصمـه محـدد**\n\n"
    "**⎞𝟑⎝** `.بصماتي`\n"
    "**•• لـ عـرض قائمـة بـ جميـع بصمـاتك المضـافـه**\n\n"
    "**⎞𝟒⎝** `.حذف بصماتي`\n"
    "**•• لـ حـذف جميـع بصمـاتك المضافـه**\n\n"
    "\n 𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](t.me/Repthon) 𓆪"
)


# R
@zq_lo.rep_cmd(pattern="البصمات")
async def cmd(baqir):
    await edit_or_reply(baqir, BaqirMeMe_cmd)

async def reply_id(event):
    reply_to_id = None
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    return reply_to_id

@zq_lo.on(admin_cmd(incoming=True))
async def filter_incoming_handler(event):
    name = event.raw_text
    repl = await reply_id(event)
    filters = get_pasmats(zq_lo.uid)
    if not filters:
        return
    for trigger in filters:
        if name == trigger.keyword:
            file_media = None
            filter_msg = None
            if trigger.f_mesg_id:
                msg_o = await event.client.get_messages(
                    entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id)
                )
                file_media = msg_o.media
                filter_msg = msg_o.message
                link_preview = True
            elif trigger.reply:
                filter_msg = trigger.reply
                link_preview = False
            try:
                await event.client.send_file(
                    event.chat_id,
                    file=file_media,
                    link_preview=link_preview,
                    reply_to=repl,
                )
                await event.delete()
            except BaseException:
                return

@zq_lo.rep_cmd(pattern="بصمه (.*)")
async def add_new_meme(event):
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**⪼ البصمـات 🔊 :**\
                \n**⪼ تم حفـظ البصمـه بـ اسم {keyword}**\n**⪼ لـ قائمـه بصماتك .. بنجـاح ✅**\n**⪼ لـ تصفـح قائمـة بصماتك ارسـل (.بصماتي) 📑**",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID,
                messages=msg,
                from_peer=event.chat_id,
                silent=True,
            )
            msg_id = msg_o.id
        else:
            await edit_or_reply(
                event,
                "**❈╎يتطلب اضافة البصمات تعيين كـروب السجـل اولاً ..**\n**❈╎لاضافـة كـروب السجـل**",
            )
            return
    elif msg and msg.text and not string:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**")
    elif not string:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**")
    else:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**")
    success = "**⪼تم {} البصمـه بـ اسم {} .. بنجـاح ✅**"
    if add_pasmat(str(zq_lo.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("اضافة", keyword))
    remove_pasmat(str(zq_lo.uid), keyword)
    if add_pasmat(str(zq_lo.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("تحديث", keyword))
    await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**")


@zq_lo.rep_cmd(pattern="بصماتي$")
async def on_meme_list(event):
    OUT_STR = "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**"
    filters = get_pasmats(zq_lo.uid)
    for filt in filters:
        if OUT_STR == "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**":
            OUT_STR = "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 - قائمـة بصمـاتك المضـافـة 🔊𓆪\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
        OUT_STR += "🎙 `{}`\n".format(filt.keyword)
    await edit_or_reply(
        event,
        OUT_STR,
        caption="**⧗╎قائمـة بصمـاتك المضـافـه🔊**",
        file_name="filters.text",
    )


@zq_lo.rep_cmd(pattern="حذف بصمه(?: |$)(.*)")
async def remove_a_meme(event):
    filt = event.pattern_match.group(1)
    if not remove_pasmat(zq_lo.uid, filt):
        await event.edit("**- ❝ البصمـه ↫** {} **غيـر موجـوده ⁉️**".format(filt))
    else:
        await event.edit("**- ❝ البصمـه ↫** {} **تم حذفهـا بنجاح ☑️**".format(filt))


@zq_lo.rep_cmd(pattern="حذف بصماتي$")
async def on_all_meme_delete(event):
    filters = get_pasmats(zq_lo.uid)
    if filters:
        remove_all_pasmats(zq_lo.uid)
        await edit_or_reply(event, "**⪼ تم حـذف جميـع بصمـاتك .. بنجـاح ✅**")
    else:
        OUT_STR = "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لاضافتهـا لـ قائمـة بصماتك 🧾**"
        await edit_or_reply(event, OUT_STR)
