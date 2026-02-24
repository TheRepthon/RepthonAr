import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import (
    NoActiveGroupCall,
    NotInCallError,
)
from pytgcalls.types import MediaStream, StreamEnded

from telethon import functions
from telethon.errors import ChatAdminRequiredError
from telethon.errors.rpcerrorlist import ChannelInvalidError

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

        try:
            await self.app.join_group_call(
                chat.id,
                MediaStream(audio="baqir/baqir/Silence01s.mp3"),
                join_as=join_as,
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

        self.CHAT_ID = chat.id
        self.CHAT_NAME = chat.title

        return f"✅ تم الانضمام إلى المكالمة في {chat.title}"

    
    async def leave_vc(self):
        try:
            await self.app.leave_group_call(self.CHAT_ID)
        except NotInCallError:
            pass

        self.clear_vars()

    
    async def play_song(self, path, video=False):
        if not self.CHAT_ID:
            return "⚠️ لست داخل مكالمة صوتية"

        track = {
            "path": path,
            "video": video,
        }

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
            await self.app.change_stream(
                self.CHAT_ID,
                MediaStream(audio="baqir/baqir/Silence01s.mp3"),
            )
            return "⚠️ قائمة التشغيل فارغة"
        next_track = self.PLAYLIST.pop(0)
        if next_track["video"]:
            stream = MediaStream(
                audio=next_track["path"],
                video=next_track["path"],
            )
        else:
            stream = MediaStream(audio=next_track["path"])
            await self.app.change_stream(self.CHAT_ID, stream)
            self.PLAYING = next_track
            return "🎵 تم تشغيل المقطع"
        
        async def pause(self):
        if not self.PLAYING:
            return "⚠️ لا يوجد شيء يعمل"
            await self.app.pause_stream(self.CHAT_ID)
            self.PAUSED = True
            return "⏸ تم الإيقاف المؤقت"
        
        async def resume(self):
            if not self.PLAYING:
                return "⚠️ لا يوجد شيء يعمل"
                await self.app.resume_stream(self.CHAT_ID)
                self.PAUSED = False
                return "▶️ تم الاستئناف"
