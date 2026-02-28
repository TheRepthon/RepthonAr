import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, StreamEnded
from pytgcalls.exceptions import NoActiveGroupCall
from telethon import functions, utils
from telethon.errors import ChatAdminRequiredError
from telethon.errors.rpcerrorlist import ChannelInvalidError
from repthon import zq_lo
from ..vc_baqir.stream_helper import Stream
from ..Config import Config

vc_session = Config.VC_SESSION


class RepVC:
    def __init__(self, client):
        self.client = client
        self.app = PyTgCalls(client)

        self.CHAT_ID = None
        self.CHAT_NAME = None

        self.PLAYING = None
        self.PLAYLIST = []

        self.PAUSED = False
        self.LOCK = asyncio.Lock()
        self.STREAM_READY = False


    async def start(self):
        await self.app.start()

        @self.app.on_update()
        async def handler(_, update):
            if isinstance(update, StreamEnded):
                if self.PLAYING:
                    await asyncio.sleep(1)
                    if self.PLAYING:
                        await self._safe_skip()


    async def join_vc(self, chat):
        if self.CHAT_ID:
            await self.leave_vc()

        real_id = utils.get_peer_id(chat)

        try:
            await self.app.play(
                real_id,
                MediaStream("baqir/baqir/Silence01s.mp3")
            )

        except NoActiveGroupCall:
            try:
                await self.client(
                    functions.phone.CreateGroupCallRequest(
                        peer=chat,
                        title="مكالمة صوتية",
                    )
                )
                await asyncio.sleep(2)
                return await self.join_vc(chat)

            except ChatAdminRequiredError:
                return "⚠️ تحتاج صلاحيات مشرف"
            except ChannelInvalidError:
                return "⚠️ الحساب المساعد غير موجود"

        self.CHAT_ID = real_id
        self.CHAT_NAME = chat.title

        await asyncio.sleep(2)

        self.STREAM_READY = True

        return f"✅ تم الانضمام إلى {chat.title}"


    async def leave_vc(self):
        try:
            await self.app.leave_group_call(self.CHAT_ID)
        except Exception:
            pass

        self.CHAT_ID = None
        self.CHAT_NAME = None
        self.PLAYING = None
        self.PLAYLIST.clear()
        self.PAUSED = False
        self.STREAM_READY = False


    async def play_song(self, path, force=False):

        if not self.CHAT_ID:
            return "⚠️ لست داخل مكالمة"

        track = {"path": path}

        async with self.LOCK:

            if force:
                self.PLAYLIST.insert(0, track)
                return await self._safe_skip()

            if self.PLAYING:
                self.PLAYLIST.append(track)
                return f"📌 أضيف للقائمة ({len(self.PLAYLIST)})"

            self.PLAYLIST.append(track)
            return await self._safe_skip()


    async def _safe_skip(self):
    async with self.LOCK:
        if not self.PLAYLIST:
            self.PLAYING = None
            return "⚠️ انتهت القائمة"

        next_track = self.PLAYLIST.pop(0)

        try:
            stream = MediaStream(next_track["path"])

            await self.app.play(
                self.CHAT_ID,
                stream
            )

            self.PLAYING = next_track
            return "🎵 تم التشغيل"

        except Exception as e:
            self.PLAYING = None
            return f"❌ خطأ في التشغيل:\n{e}"

    async def skip(self):
        return await self._safe_skip()


    async def pause(self):
        if not self.PLAYING:
            return "⚠️ لا يوجد شيء يعمل"

        await self.app.pause_stream(self.CHAT_ID)
        self.PAUSED = True
        return "⏸ تم الإيقاف"

    async def resume(self):
        if not self.PLAYING:
            return "⚠️ لا يوجد شيء يعمل"

        await self.app.resume_stream(self.CHAT_ID)
        self.PAUSED = False
        return "▶️ تم الاستئناف"
