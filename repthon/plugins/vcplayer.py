# Team Repthon

import asyncio
import logging

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import User

from repthon import zq_lo
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply

from ..vc_baqir.stream_helper import Stream, search_youtube
from ..vc_baqir.tg_downloader import tg_dl
from ..vc_baqir.vcp_helper import RepVC


plugin_category = "المكالمات"

logging.getLogger("pytgcalls").setLevel(logging.ERROR)

vc_session = Config.VC_SESSION

if vc_session:
    vc_client = TelegramClient(
        StringSession(vc_session), Config.API_ID, Config.API_HASH
    )
else:
    vc_client = zq_lo

vc_client.__class__.__module__ = "telethon.client.telegramclient"

vc_player = RepVC(vc_client)
asyncio.create_task(vc_player.start())

# ================= JOIN =================

@zq_lo.rep_cmd(pattern="انضمام$")
async def joinVoicechat(event):
    await edit_or_reply(event, "⚈ جاري الانضمام ...")

    if vc_player.CHAT_ID:
        return await edit_delete(event, "⚈ انت منضم مسبقاً")

    try:
        chat = await zq_lo.get_entity(event.chat_id)
    except Exception as e:
        return await edit_delete(event, f"خطأ:\n{e}")

    if isinstance(chat, User):
        return await edit_delete(event, "⚈ لا يمكن تشغيل مكالمة هنا")

    out = await vc_player.join_vc(chat)
    await edit_delete(event, out)

# ================= LEAVE =================

@zq_lo.rep_cmd(pattern="خروج$")
async def leaveVoicechat(event):
    if not vc_player.CHAT_ID:
        return await edit_delete(event, "⚈ لست داخل مكالمة")

    await edit_or_reply(event, "⚈ جاري المغادرة ...")
    name = vc_player.CHAT_NAME
    await vc_player.leave_vc()
    await edit_delete(event, f"⚈ تم مغادرة {name}")

# ================= PLAY AUDIO =================

@zq_lo.rep_cmd(pattern="شغل(?: |$)(.*)")
async def play_audio(event):

    query = event.pattern_match.group(1)

    if not vc_player.CHAT_ID:
        return await edit_delete(event, "⚈ انضم اولاً عبر .انضمام")

    if event.reply_to_msg_id and not query:
        query = await tg_dl(event)

    if not query:
        return await edit_delete(event, "⚈ اكتب اسم اغنية او رابط")

    # بحث اذا ليس رابط
    if not query.startswith("http"):
        query = await search_youtube(query)

    await edit_or_reply(event, "🎧 جاري التشغيل ...")

    resp = await vc_player.play_song(
        path=query,
        stream_type=Stream.audio,
        force=False
    )

    await edit_delete(event, resp, time=20)

# ================= PLAY VIDEO =================

@zq_lo.rep_cmd(pattern="شغل فيديو(?: |$)(.*)")
async def play_video(event):

    query = event.pattern_match.group(1)

    if not vc_player.CHAT_ID:
        return await edit_delete(event, "⚈ انضم اولاً عبر .انضمام")

    if event.reply_to_msg_id and not query:
        query = await tg_dl(event)

    if not query:
        return await edit_delete(event, "⚈ اكتب اسم فيديو او رابط")

    if not query.startswith("http"):
        query = await search_youtube(query)

    await edit_or_reply(event, "📺 جاري تشغيل الفيديو ...")

    resp = await vc_player.play_song(
        path=query,
        stream_type=Stream.video,
        force=False
    )

    await edit_delete(event, resp, time=20)

# ================= SKIP =================

@zq_lo.rep_cmd(pattern="تخطي$")
async def skip_stream(event):
    if not vc_player.CHAT_ID:
        return await edit_delete(event, "⚈ لا يوجد مكالمة")

    await edit_or_reply(event, "⏭ جاري التخطي ...")
    res = await vc_player.skip()
    await edit_delete(event, res, time=20)

# ================= PAUSE =================

@zq_lo.rep_cmd(pattern="توقف$")
async def pause_stream(event):
    res = await vc_player.pause()
    await edit_delete(event, res, time=20)

# ================= RESUME =================

@zq_lo.rep_cmd(pattern="كمل$")
async def resume_stream(event):
    res = await vc_player.resume()
    await edit_delete(event, res, time=20)

# ================= PLAYLIST =================

@zq_lo.rep_cmd(pattern="قائمة التشغيل$")
async def get_playlist(event):

    if not vc_player.PLAYLIST:
        return await edit_delete(event, "⚈ القائمة فارغة", time=15)

    rep = ""
    for i, item in enumerate(vc_player.PLAYLIST, 1):
        kind = "🎵" if item["stream_type"] == Stream.audio else "📺"
        rep += f"{i}- {kind} {item['path']}\n"

    await edit_delete(event, f"⚈ قائمة التشغيل:\n\n{rep}", time=40)

Music_cmd = (
    "[ᯓ 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - اوامــر الميـوزك 🎸](t.me/Repthon) ."
    "**⋆─┄─┄─┄─┄──┄─┄─┄─┄─⋆**\n"
    "⚉ `.شغل`\n"
    "**⪼ الامـر + (كلمـة او رابـط) او بالـرد ع مقطـع صوتـي**\n"
    "⚉ `.شغل فيديو`\n"
    "**⪼ الامـر + (كلمـة او رابـط) او بالـرد ع مقطـع فيديـو**\n\n"
    "**Ⓜ️ اوامـر تشغيـل اجباريـه مـع تخطـي قائمـة التشغيـل :**\n"
    "⚉ `.شغل 1`\n"
    "**⪼ الامـر + (كلمـة او رابـط) او بالـرد ع مقطـع صوتـي**\n"
    "⚉ `.شغل فيديو 1`\n"
    "**⪼ الامـر + (كلمـة او رابـط) او بالـرد ع مقطـع فيديـو**\n\n"
    "⚉ `.قائمة التشغيل`\n"
    "⚉ `.توقف`\n"
    "⚉ `.كمل`\n"
    "⚉ `.تخطي`\n\n"
    "⚉ `.انضمام`\n"
    "⚉ `.خروج`"
)

@zq_lo.rep_cmd(pattern="الميوزك")
async def cmd(banen):
    await edit_or_reply(banen, Music_cmd)

@zq_lo.rep_cmd(pattern="ميوزك")
async def cmd(ba):
    await edit_or_reply(ba, Music_cmd)
