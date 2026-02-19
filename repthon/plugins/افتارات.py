#𝐑𝐞𝐩𝐭𝐡𝐨𝐧 ®
#الملـف حقـوق وكتابـة باقر ⤶ @E_7_V خاص بسـورس ⤶ 𝐑𝐞𝐩𝐭𝐡𝐨𝐧

import asyncio
import os
from secrets import choice
import random
from urllib.parse import quote_plus
from collections import deque
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import InputMessagesFilterVideo, InputMessagesFilterVoice, InputMessagesFilterPhotos

from repthon import zq_lo

from ..core.logger import logging
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.styles.meme.meme import rvois
from . import ALIVE_NAME, mention
from ..helpers import get_user_from_event
from ..helpers.utils import _format

from . import reply_id as rd


@zq_lo.rep_cmd(pattern="حالات$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل حـالات واتـس ...**")
    try:
        REPTHON = [
            baqir
            async for baqir in event.client.iter_messages(
                "@RSHDO5", filter=InputMessagesFilterVideo
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(REPTHON),
            caption=f"**🎆┊حـالات واتـس قصيـرة 🧸♥️**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="ستوري انمي$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الستـوري ...**")
    try:
        REPTHON = [
            baqir
            async for baqir in event.client.iter_messages(
                "@AA_Zll", filter=InputMessagesFilterVideo
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(REPTHON),
            caption=f"**🎆┊ستـوريات آنمـي قصيـرة 🖤🧧**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="رقيه$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الرقيـه ...**")
    try:
        repgan = [
            baqir
            async for baqir in event.client.iter_messages(
                "@Rqy_1", filter=InputMessagesFilterVoice
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(repgan),
            caption=f"**◞مقاطـع رقيـه شرعيـة ➧🕋🌸◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="رمادي$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الافتـار ...**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@shababbbbR", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**◞افتـارات شبـاب ࢪمـاديه ➧🎆🖤◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="رماديه$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الافتـار ...**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@banatttR", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**◞افتـارات بنـات ࢪمـاديه ➧🎆🤎◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="بيست$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...🧚🏻‍♀🧚🏻‍♀╰**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@Tatkkkkkim", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**◞افتـارات بيست تطقيـم بنـات ➧🎆🧚🏻‍♀🧚🏻‍♀◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="حب$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...♥️╰**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@tatkkkkkimh", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**◞افتـارات حـب تمبلـرࢪ ➧🎆♥️◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="رياكشن$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الرياكشـن ...**")
    try:
        REPTHON = [
            baqir
            async for baqir in event.client.iter_messages(
                "@reagshn", filter=InputMessagesFilterVideo
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(REPTHON),
            caption=f"** 🎬┊رياكشـن تحشيـش ➧🎃😹◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="ادت$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل مقطـع ادت ...**")
    try:
        REPTHON = [
            baqir
            async for baqir in event.client.iter_messages(
                "@snje1", filter=InputMessagesFilterVideo
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(REPTHON),
            caption=f"**🎬┊مقاطـع ايـدت منوعـه ➧ 🖤🎭◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="غنيلي$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الاغنيـه ...𓅫╰**")
    try:
        repgan = [
            baqir
            async for baqir in event.client.iter_messages(
                "@TEAMSUL", filter=InputMessagesFilterVoice
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(repgan),
            caption=f"**✦┊تم اختياࢪ الاغنيـه لك 💞🎶**ٴ▁ ▂ ▉ ▄ ▅ ▆ ▇ ▅ ▆ ▇ █ ▉ ▂ ▁\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")
        

@zq_lo.rep_cmd(pattern="شعر$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الشعـر ...**")
    try:
        repgan = [
            baqir
            async for baqir in event.client.iter_messages(
                "@L1BBBL", filter=InputMessagesFilterVoice
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(repgan),
            caption=f"**✦┊تم اختيـار مقطـع الشعـر هـذا لك**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="ميمز$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الميمـز ...**")
    try:
        repgan = [
            baqir
            async for baqir in event.client.iter_messages(
                "@MemzWaTaN", filter=InputMessagesFilterVoice
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(repgan),
            caption=f"**✦┊تم اختيـار مقطـع الميمـز هـذا لك**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="ري اكشن$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الرياكشـن ...**")
    try:
        repre = [
            baqir
            async for baqir in event.client.iter_messages(
                "@gafffg", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(repre),
            caption=f"**🎆┊رياكشـن تحشيـش ➧🎃😹◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="معلومه$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل صـورة ومعلومـة ...**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@A_l3l", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**🎆┊صـورة ومعلومـة ➧ 🛤💡◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="تويت$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ كـت تـويت بالصـور ...**")
    try:
        repre = [
            baqir
            async for baqir in event.client.iter_messages(
                "@twit_selva", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(repre),
            caption=f"**✦┊كـت تـويت بالصـور ➧⁉️🌉◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="خيرني$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮•⎚ لـو خيـروك بالصـور ...**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@SourceSaidi", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**✦┊لـو خيـروك  ➧⁉️🌉◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="ولد انمي$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...𓅫╰**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@dnndxn", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**◞افتـارات آنمي شبـاب ➧🎆🙋🏻‍♂◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="بنت انمي$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...𓅫╰**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@shhdhn", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**◞افتـارات آنمي بنـات ➧🎆🧚🏻‍♀◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="بنات$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...𓅫╰**")
    try:
        reph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@banaaaat1", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(reph),
            caption=f"**◞افتـارات بنـات تمبلـرࢪ ➧🎆🧚🏻‍♀◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="كرة$")
async def _(event):
    repevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...𓅫╰**")
    try:
        repph = [
            baqir
            async for baqir in event.client.iter_messages(
                "@xy_89y", filter=InputMessagesFilterPhotos
            )
        ]
        aing = await event.client.get_me()
        await event.client.send_file(
            event.chat_id,
            file=random.choice(repph),
            caption=f"**◞افتـارات كــرة قـدم ➧🎆⚽◟**\n\n[➧𝙎𝙤𝙪𝙧𝙘𝙚 𝙍𝙀𝙋𝙏𝙃𝙊𝙉](https://t.me/Repthon)",
        )
        await repevent.delete()
    except Exception:
        await repevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")


@zq_lo.rep_cmd(pattern="ص(\\d+)$")
async def rvois_handler(vois):
    if vois.fwd_from:
        return
    Re = await rd(vois)
    match = vois.pattern_match.group(1)
    idx = int(match) - 1
    if 0 <= idx < len(rvois):
        await vois.client.send_file(vois.chat_id, rvois[idx], reply_to=Re)
        await vois.delete()
