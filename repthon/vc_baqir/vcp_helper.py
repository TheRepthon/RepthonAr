import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import NoActiveGroupCall, NotInCallError
from pytgcalls.types import MediaStream, StreamEnded
from telethon import functions, utils
from telethon.errors import ChatAdminRequiredError
from telethon.errors.rpcerrorlist import ChannelInvalidError
from repthon import zq_lo
from ..vc_baqir.stream_helper import Stream
from ..Config import Config

vc_session = Config.VC_SESSION

class RepVC:
    def __init__(self, client) -> None:
        self.client = client
        self.app = PyTgCalls(client)
        self.CHAT_ID = None
        self.CHAT_NAME = None
        self.PLAYING = None
        self.PLAYLIST = []
        self.PAUSED = False

    async def start(self):
        await self.app.start()
        @self.app.on_update()
        async def stream_handler(_, update):
            if isinstance(update, StreamEnded):
                await self.skip()

    def clear_vars(self):
        self.CHAT_ID = None
        self.CHAT_NAME = None
        self.PLAYING = None
        self.PLAYLIST = []
        self.PAUSED = False

    async def join_vc(self, chat, join_as=None):
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
                return await self.join_vc(chat, join_as)
            except ChatAdminRequiredError:
                return "⚉ تحتاج صلاحيات مشرف لبدء مكالمة صوتية"
            except ChannelInvalidError:
                return "⚉ الحساب المساعد غير موجود في المجموعة"
        self.CHAT_ID = real_id
        self.CHAT_NAME = chat.title
        return f"✅ تم الانضمام إلى المكالمة في {chat.title}"

    async def leave_vc(self):
        try:
            await self.app.leave_group_call(self.CHAT_ID)
        except Exception:
            pass
        self.clear_vars()

    async def play_song(self, path, stream_type, force=False):
        if not self.CHAT_ID:
            return "⚠️ لست داخل مكالمة صوتية"
        
        track = {"path": path, "stream_type": stream_type}
        
        if force:
            self.PLAYLIST.insert(0, track)
            return await self.skip()
        
        if self.PLAYING:
            self.PLAYLIST.append(track)
            return f"📌 تمت الإضافة لقائمة التشغيل ({len(self.PLAYLIST)})"
            
        self.PLAYLIST.append(track)
        return await self.skip()

    async def skip(self, clear=False):
        if clear:
            self.PLAYLIST.clear()
        if not self.PLAYLIST:
            self.PLAYING = None
            try:
                await self.app.play(self.CHAT_ID, MediaStream("baqir/baqir/Silence01s.mp3"))
            except Exception:
                pass
            return "⚠️ قائمة التشغيل فارغة"
            
        next_track = self.PLAYLIST.pop(0)
        if next_track["stream_type"] == Stream.video:
             stream = MediaStream(next_track["path"]) 
        else:
             stream = MediaStream(next_track["path"])
            
        await self.app.play(self.CHAT_ID, stream)
        self.PLAYING = next_track
        return "🎵 تم تشغيل المقطع"

    async def pause(self):
        if not self.PLAYING: return "⚠️ لا يوجد شيء يعمل"
        await self.app.pause_stream(self.CHAT_ID)
        self.PAUSED = True
        return "⏸ تم الإيقاف المؤقت"
        
    async def resume(self):
        if not self.PLAYING: return "⚠️ لا يوجد شيء يعمل"
        await self.app.resume_stream(self.CHAT_ID)
        self.PAUSED = False
        return "▶️ تم الاستئناف"
