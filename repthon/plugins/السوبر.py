import os
import re
import asyncio
import random
import time
import math
import base64
import contextlib
import shutil
import urllib3
import requests
import string
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from telethon.utils import get_display_name
from urlextract import URLExtract


from catbox import CatboxUploader
    
from telethon import events, types
from telethon.utils import get_peer_id, get_display_name
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl import functions, types
from telethon.tl.types import Channel, Chat, InputPhoto, User, InputMessagesFilterEmpty
from telethon.tl.functions.channels import GetParticipantRequest, GetFullChannelRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.errors import ChannelInvalidError, ChannelPrivateError, ChannelPublicGroupNaError, BadRequestError, ChatAdminRequiredError, FloodWaitError, MessageNotModifiedError, UserAdminInvalidError
from telethon.errors.rpcerrorlist import ForbiddenError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetStickerSetRequest, ExportChatInviteRequest
from telethon.tl.functions.messages import ImportChatInviteRequest as Get

from . import zq_lo

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import media_type, unsavegif, progress
from ..helpers.utils import _reptools, _reputils, _format, parse_pre, reply_id
from ..sql_helper.autopost_sql import add_post, get_all_post, is_post, remove_post
from ..sql_helper.echo_sql import addecho, get_all_echos, get_echos, is_echo, remove_all_echos, remove_echo, remove_echos
from ..core.data import blacklist_chats_list
from ..sql_helper import global_collectionjson as sql
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID
from . import *

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)

NASHR = gvarstatus("R_NASHR") or "(نشر عام|سوبر)"
#SPRS = gvarstatus("R_SPRS") or "(نشر_تلقائي|نشر|تلقائي)"
#OFSPRS = gvarstatus("R_OFSPRS") or "(ايقاف_النشر|ايقاف النشر|ستوب)"

SP_BLACKLIST = [
    "مساعدة ريبثون - Support Repthon",
    "كـروب السجـل ريبـــثون",
    "مجمـوعـة التخـزين",
    ]

r_super = False
client = zq_lo
opened = True
closed = False

extractor = URLExtract()
telegraph = Telegraph()
r = telegraph.create_account(short_name=Config.TELEGRAPH_SHORT_NAME)
auth_url = r["auth_url"]
uploader = CatboxUploader()

def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")

# قائمة بأسماء المتغيرات
su_variables = ["Super_Id1", "Super_Id2", "Super_Id3", "Super_Id4", "Super_Id5", "Super_Id6", "Super_Id7", "Super_Id8", "Super_Id9", "Super_Id10",
             "Super_Id11", "Super_Id12", "Super_Id13", "Super_Id14", "Super_Id15", "Super_Id16", "Super_Id17", "Super_Id18", "Super_Id19", "Super_Id20"]

BaqirNSH_cmd = (
    "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 - اوامـر النشـر التلقـائي 𓆪\n\n"
    "**- اضغـط ع الامـر للنسـخ** \n\n\n"
    "**⪼** `.السوبر` \n"
    "**- لـ عـرض اوامـر النشـر في السـوبـرات**\n\n"
    "**⪼** `.تلقائي` \n"
    "**- الامـر + (معـرف/ايـدي/رابـط) القنـاة المـراد النشـر التلقـائي منهـا** \n"
    "**- استخـدم الامـر بقنـاتـك \n\n\n"
    "**⪼** `.ايقاف تلقائي` \n"
    "**- الامـر + (معـرف/ايـدي/رابـط) القنـاة المـراد ايقـاف النشـر التلقـائي منهـا** \n"
    "**- استخـدم الامـر بقنـاتـك \n\n\n"
    "**- ملاحظـه :**\n"
    "**- الاوامـر صـارت تدعـم المعـرفات والروابـط الى جـانب الايـدي 🏂🎗**\n"
    "**🛃 سيتـم اضـافة المزيـد من اوامــر النشـر التلقـائي بالتحديثـات الجـايه**\n"
)

BaqirSuper_cmd = (
    "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 النشـࢪ التڪࢪاࢪي\n"
    "**⋆┄─┄─┄─┄─┄─┄─┄─┄⋆**\n"
    "**✧ قـائمـة اوامـر السـوبـر (النشـر التلقائي) ♾ :**\n\n"
    "`.اوامر مكرر`\n"
    "**⪼ لـ عـرض اوامـر النشـر التلقائـي (.مكرر) المحدثه بدون بانـد ...✓**\n\n" 
    "ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
    "`.سوبر`\n"
    "**⪼ استخـدام الامـر ( .سوبر + عـدد الثـوانـي )**\n"
    "**⪼ بالـرد ع الرسـالة المـراد نشرهـا**\n" 
    "**⪼ لـ النشـر بـ جميـع سوبـرات حسابك التي تشتمـل ع كلمـة سـوبر او Super ...✓**\n\n" 
    "ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
    "`.نشر`\n"
    "**⪼ استخـدام الامـر ( .نشر + عـدد الثـوانـي )**\n"
    "**⪼ بالـرد ع الرسـالة المـراد نشرهـا**\n" 
    "**⪼ لـ النشـر بـ مجموعـة محـددة او عـدة سـوبرات مضافه مسبقاً عبر (.اضف سوبر) ...✓**\n\n"
    "`.اضف سوبر`\n"
    "**⪼ استخـدم الامـر داخـل المجموعـة المحـدده ...**\n"
    "**⪼ او استخـدم (الامـر + ايدي السوبـر) لـ اضافـة عـدة سـوبـرات الـى القائمـة ...**\n"
    "**⪼ لـ اضافة مجموعـة محـددة لـ قائمـة مجموعات النشـر ...✓**\n\n"
    "`.حذف سوبر`\n"
    "**⪼ استخـدم الامـر داخـل المجموعـة المحـدده ...**\n"
    "**⪼ او استخـدم (الامـر + ايدي السوبـر) لـ حـذف السـوبـر مـن القائمـة ...**\n"
    "**⪼ لـ حـذف مجموعـة محـددة مـن قائمـة كروبات النشر ...✓**\n\n"
    "`.السوبرات`\n"
    "**⪼ لـ جلب قائمـة مجموعـات النشـر التي سبق اضافتها ...✓**\n\n"
    "ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
    "`.نشر_عام`\n"
    "**⪼ استخـدام الامـر ( .نشر_عام + عـدد الثـوانـي )**\n"
    "**⪼ بالـرد ع الرسـالة المـراد نشرهـا**\n" 
    "**⪼ لـ النشـر بـ جميـع المجموعات الموجودة ع حسابك ...✓**\n\n"
    "ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
    "`.ايقاف النشر`\n"
    "**⪼ لـ إيقـاف جميـع عمليـات النشـر التلقائـي ...✓**\n\n"
    "ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
    "**⪼ مـلاحظــه هـامــه :**\n"
    "- اوامـر النشـر راجعـة لـ إستخـدامك انت .. السـورس غيـر مسـؤول عـن أي باند او حظر لـ الحسابات المستخدمه نشـر تلقائي من قبـل تيليجـرام <=> لذلك وجب التنبيـه ⚠️\n"
    "ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
)

async def get_chatinfo(chat):
    chat_info = None
    chat = int(chat)
    try:
        chat_info = await zq_lo(GetFullChatRequest(chat))
    except BaseException:
        try:
            chat_info = await zq_lo(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            chat_info = "**✧ لـم يتـمّ العثـور على القنـاة/المجموعـة ✕**"
            return None
        except ChannelPrivateError:
            chat_info = "**✧ هـذه مجموعـة أو قنـاة خاصـة أو لقد تمّ حظـري منه ⛞**"
        except ChannelPublicGroupNaError:
            chat_info = "**✧ القنـاة أو المجموعـة الخارقـة غيـر موجـودة ✕**"
        except (TypeError, ValueError) as err:
            LOGS.info(err)
            chat_info = "**✧ لم يتم العثور على المجموعة او القناة**"
    return chat_info


### قسم مكرر ###
SPAM = gvarstatus("RR_SPAM") or "(مؤقت1|مكرر1)"
UNSPAM = gvarstatus("RR_UNSPAM") or "(ايقاف مؤقت1|ايقاف مكرر1)"

### قسم مكرر2 ###
SP2AM = gvarstatus("RR_SP2AM") or "(مؤقت2|مكرر2)"
UNSP2AM = gvarstatus("RR_UNSP2AM") or "(ايقاف مؤقت2|ايقاف مكرر2)"

### قسم مكرر3 ###
SP3AM = gvarstatus("RR_SP3AM") or "(مؤقت3|مكرر3)"
UNSP3AM = gvarstatus("RR_UNSP3AM") or "(ايقاف مؤقت3|ايقاف مكرر3)"


# قائمة بأسماء المتغيرات للامر .مكرر
sp_variables = ["SppSuper_Id1", "SppSuper_Id2", "SppSuper_Id3", "SppSuper_Id4", "SppSuper_Id5", "SppSuper_Id6", "SppSuper_Id7", "SppSuper_Id8", "SppSuper_Id9", "SppSuper_Id10",
             "SppSuper_Id11", "SppSuper_Id12", "SppSuper_Id13", "SppSuper_Id14", "SppSuper_Id15", "SppSuper_Id16", "SppSuper_Id17", "SppSuper_Id18", "SppSuper_Id19", "SppSuper_Id20"]

# قائمة بأسماء المتغيرات للامر .مكرر2
sp2_variables = ["Spp2Super_Id1", "Spp2Super_Id2", "Spp2Super_Id3", "Spp2Super_Id4", "Spp2Super_Id5", "Spp2Super_Id6", "Spp2Super_Id7", "Spp2Super_Id8", "Spp2Super_Id9", "Spp2Super_Id10",
             "Spp2Super_Id11", "Spp2Super_Id12", "Spp2Super_Id13", "Spp2Super_Id14", "Spp2Super_Id15", "Spp2Super_Id16", "Spp2Super_Id17", "Spp2Super_Id18", "Spp2Super_Id19", "Spp2Super_Id20"]

# قائمة بأسماء المتغيرات للامر .مكرر3
sp3_variables = ["Spp3Super_Id1", "Spp3Super_Id2", "Spp3Super_Id3", "Spp3Super_Id4", "Spp3Super_Id5", "Spp3Super_Id6", "Spp3Super_Id7", "Spp3Super_Id8", "Spp3Super_Id9", "Spp3Super_Id10",
             "Spp3Super_Id11", "Spp3Super_Id12", "Spp3Super_Id13", "Spp3Super_Id14", "Spp3Super_Id15", "Spp3Super_Id16", "Spp3Super_Id17", "Spp3Super_Id18", "Spp3Super_Id19", "Spp3Super_Id20"]

r_spnasher = False
r_sp2nasher = False
r_sp3nasher = False


BaqirSpsuper_cmd = (
"ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 النشـࢪ التڪࢪاࢪي (مكࢪࢪ)\n"
"**⋆┄─┄─┄─┄─┄─┄─┄─┄⋆**\n"
"**✧ قـائمـة اوامـر النشـر التلقائي (مكرر1) ♾ :**\n\n"
"`.مكرر1`\n"
"**⪼ استخـدام الامـر ( .مكرر1 + عـدد الثـوانـي )**\n"
"**⪼ بالـرد ع الرسـالة المـراد نشرهـا**\n" 
"**⪼ لـ النشـر بـ مجموعـة محـددة او عـدة سـوبرات مضافه مسبقاً عبر (.اضف مكرر1) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.اضف مكرر1`\n"
"**⪼ استخـدم الامـر داخـل المجموعـة المحـدده ...**\n"
"**⪼ او استخـدم (الامـر + ايدي المجموعة) لـ اضافـة عـدة مجموعات الـى قائمـة مكـرر1 ...**\n"
"**⪼ لـ اضافة مجموعـة محـددة لـ قائمـة مجموعات النشـر (مكرر1) ...✓**\n\n"
"`.حذف مكرر1`\n"
"**⪼ استخـدم الامـر داخـل المجموعـة المحـدده ...**\n"
"**⪼ او استخـدم (الامـر + ايدي المجموعة) لـ حـذف المجموعة مـن قائمـة مكـرر1 ...**\n"
"**⪼ لـ حـذف مجموعـة محـددة مـن قائمـة كروبات النشر (مكرر1) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.قائمة مكرر1`\n"
"**⪼ لـ جلب قائمـة مجموعـات النشـر التي سبق اضافتها لـ الامـر (مكرر1) ...✓**\n\n"
"`.حذف قائمة مكرر1`\n"
"**⪼ لـ حذف جميـع مجموعـات النشـر التي سبق اضافتها لـ قائمـة الامـر (مكرر1) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.ايقاف مكرر1`\n"
"**⪼ لـ إيقـاف جميـع عمليـات النشـر التلقائـي الخاصه بالامـر (.مكرر1)...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"**⪼ مـلاحظــه هـامــه :**\n"
"- اوامـر النشـر راجعـة لـ إستخـدامك انت .. السـورس غيـر مسـؤول عـن أي باند او حظر في حال صار لـ الحسابات المستخدمه نشـر تلقائي <=> لذلك وجب التنبيـه ⚠️\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
)


BaqirSp2super_cmd = (
"ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 النشـࢪ التڪࢪاࢪي (مكـࢪࢪ2)\n"
"**⋆┄─┄─┄─┄─┄─┄─┄─┄⋆**\n"
"**✧ قـائمـة اوامـر النشـر التلقائي (مكرر2) الإضافيـه ♾ :**\n\n"
"`.مكرر2`\n"
"**⪼ استخـدام الامـر ( .مكرر2 + عـدد الثـوانـي )**\n"
"**⪼ بالـرد ع الرسـالة المـراد نشرهـا**\n" 
"**⪼ لـ النشـر بـ مجموعـة محـددة او عـدة سـوبرات مضافه مسبقاً عبر (.اضف مكرر2) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.اضف مكرر2`\n"
"**⪼ استخـدم الامـر داخـل المجموعـة المحـدده ...**\n"
"**⪼ او استخـدم (الامـر + ايدي المجموعة) لـ اضافـة عـدة مجموعات الـى قائمـة مكـرر ...**\n"
"**⪼ لـ اضافة مجموعـة محـددة لـ قائمـة مجموعات النشـر (مكرر2) ...✓**\n\n"
"`.حذف مكرر2`\n"
"**⪼ استخـدم الامـر داخـل المجموعـة المحـدده ...**\n"
"**⪼ او استخـدم (الامـر + ايدي المجموعة) لـ حـذف المجموعة مـن قائمـة مكـرر ...**\n"
"**⪼ لـ حـذف مجموعـة محـددة مـن قائمـة كروبات النشر (مكرر2) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.قائمة مكرر2`\n"
"**⪼ لـ جلب قائمـة مجموعـات النشـر التي سبق اضافتها لـ الامـر (مكرر2) ...✓**\n\n"
"`.حذف قائمة مكرر2`\n"
"**⪼ لـ حذف جميـع مجموعـات النشـر التي سبق اضافتها لـ قائمـة الامـر (مكرر2) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.ايقاف مكرر2`\n"
"**⪼ لـ إيقـاف جميـع عمليـات النشـر التلقائـي الخاصه بالامـر (.مكرر2)...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"**⪼ مـلاحظــه هـامــه :**\n"
"- اوامـر النشـر راجعـة لـ إستخـدامك انت .. السـورس غيـر مسـؤول عـن أي باند او حظر في حال صار لـ الحسابات المستخدمه نشـر تلقائي <=> لذلك وجب التنبيـه ⚠️\n"
)


BaqirSp3super_cmd = (
"ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 النشـࢪ التڪࢪاࢪي (مكـࢪࢪ3)\n"
"**⋆┄─┄─┄─┄─┄─┄─┄─┄⋆**\n"
"**✧ قـائمـة اوامـر النشـر التلقائي (مكرر3) الإضافيـه ♾ :**\n\n"
"`.مكرر3`\n"
"**⪼ استخـدام الامـر ( .مكرر3 + عـدد الثـوانـي )**\n"
"**⪼ بالـرد ع الرسـالة المـراد نشرهـا**\n" 
"**⪼ لـ النشـر بـ مجموعـة محـددة او عـدة سـوبرات مضافه مسبقاً عبر (.اضف مكرر3) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.اضف مكرر3`\n"
"**⪼ استخـدم الامـر داخـل المجموعـة المحـدده ...**\n"
"**⪼ او استخـدم (الامـر + ايدي المجموعة) لـ اضافـة عـدة مجموعات الـى قائمـة مكـرر ...**\n"
"**⪼ لـ اضافة مجموعـة محـددة لـ قائمـة مجموعات النشـر (مكرر3) ...✓**\n\n"
"`.حذف مكرر3`\n"
"**⪼ استخـدم الامـر داخـل المجموعـة المحـدده ...**\n"
"**⪼ او استخـدم (الامـر + ايدي المجموعة) لـ حـذف المجموعة مـن قائمـة مكـرر ...**\n"
"**⪼ لـ حـذف مجموعـة محـددة مـن قائمـة كروبات النشر (مكرر3) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.قائمة مكرر3`\n"
"**⪼ لـ جلب قائمـة مجموعـات النشـر التي سبق اضافتها لـ الامـر (مكرر3) ...✓**\n\n"
"`.حذف قائمة مكرر3`\n"
"**⪼ لـ حذف جميـع مجموعـات النشـر التي سبق اضافتها لـ قائمـة الامـر (مكرر3) ...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"`.ايقاف مكرر3`\n"
"**⪼ لـ إيقـاف جميـع عمليـات النشـر التلقائـي الخاصه بالامـر (.مكرر3)...✓**\n\n"
"ٴ┄─┄─┄─┄┄─┄─┄─┄─┄┄\n\n"
"**⪼ مـلاحظــه هـامــه :**\n"
"- اوامـر النشـر راجعـة لـ إستخـدامك انت .. السـورس غيـر مسـؤول عـن أي باند او حظر في حال صار لـ الحسابات المستخدمه نشـر تلقائي <=> لذلك وجب التنبيـه ⚠️\n"
)


# قائمة لتخزين حالة المتغيرات
var_status = []
var2_status = []
var3_status = []

async def rrr_spnasher(zq_lo, sleeptimet, message):  # نشر عبر يوزرات المجموعات المخزنه
    media_spnasher = gvarstatus("med_spnasher") if gvarstatus("med_spnasher") else None
    msg_spnasher = gvarstatus("msg_spnasher") if gvarstatus("msg_spnasher") else None
    # تحقق من حالة كل متغير
    for var in sp_variables:
        status = gvarstatus(var)
        if (status is not None) and (status not in var_status):
            var_status.append(status)

    global r_spnasher
    r_spnasher = True
    while r_spnasher:
        if gvarstatus("status_spnasher") is None:
            break
        for chat_iid in var_status:
            if gvarstatus("status_spnasher") is None:
                break
            try:
                # Introduce random delays between 1 and sleeptimet seconds.
                # • التأخيرات العشوائية:
                # تقدم تأخيرات عشوائية بين إرسال الرسائل إلى مجموعات مختلفة.
                # وهذا يجعل نمط الإرسال أقل تجانسًا.
                await asyncio.sleep(random.uniform(2, 10))
                #await asyncio.sleep(random.uniform(1, sleeptimet))  # تعني الأعداد الأصغر (أسرع إرسالًا) (ولكن مخاطرة أعلى للحظر)
                
                #chat_iiid = chat_iid if chat_iid.startswith("-100") else f"-100{chat_iid}" 
                #chat = await zedub.get_entity(chat_iiid)
                ch_id = int(chat_iid)
                if media_spnasher is not None:
                    REP_IMG = gvarstatus("med_spnasher")
                    REP = [x for x in REP_IMG.split()]
                    PIC = random.choice(REP)
                    msg_spcaption = gvarstatus("msg_spnasher") if gvarstatus("msg_spnasher") else ""
                    await zq_lo.send_file(ch_id, PIC, caption=msg_spcaption)
                else:
                    await zq_lo.send_message(ch_id, msg_spnasher, link_preview=False)
                
                # Add a delay after each successful message send
                # يقوم بتقديم تأخير بعد كل رسالة ناجحة، مما يقلل بشكل أكبر من اندفاع النشاط
                await asyncio.sleep(random.uniform(11, 20)) # اضبط هذا النطاق بناءً على ملاحظاتك.
            
            except Exception as e:
                #print(f"drrr(143): Error in sending message to chat {chat.id}: {e}")
                # Consider adding more sophisticated error handling, like retry mechanisms
                #await asyncio.sleep(random.uniform(30, 60)) #Longer delay for errors
                #await asyncio.sleep(random.uniform(5, 10)) #Longer delay for errors
                #await zedub.send_message(BOTLOG_CHATID, f"**⌔ لا يمكن العثور على المجموعة أو الدردشة** {chat_iiid} :\n`{str(e)}`")
                pass
        
        # Wait for the specified sleeptimet before starting the next round
        await asyncio.sleep(sleeptimet)


async def rr_spnasher():
    sleeptimet = int(gvarstatus("sec_spnasher"))
    message = gvarstatus("msg_spnasher")
    await rrr_spnasher(zq_lo, sleeptimet, message)


@zq_lo.rep_cmd(pattern=f"{SPAM} ([\\s\\S]*)")
async def spammer(event):
    if gvarstatus("status_spnasher"):
        if BOTLOG:
            await event.delete()
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية (مكرر1) سابقـه مفعله**\n**✧ ارسـل** ( `.اوامر مكرر2` ) ** لـ عرض اوامـر اضافيه لـ المكـرر2**")
        else:
            return await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية (مكرر1) سابقـه مفعله**\n**✧ ارسـل** ( `.اوامر مكرر2` ) ** لـ عرض اوامـر اضافيه لـ المكـرر2**")

    if not event.reply_to_msg_id:
        await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ ارسـل الامـر بالـرد ع الرسالة المراد نشرها**")
        return

    await event.delete()
    #input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)

    # قائمة بأسماء المتغيرات
    spvariables = [f"SppSuper_Id{i}" for i in range(1, 21)] 
    # تحقق من حالة المتغيرات
    vaar_status = [gvarstatus(var) for var in spvariables]
    # تحقق من الشروط المطلوبة
    #if all(var_status[0:2]) and all(status is None for status in var_status[2:]):
    if all(vaar_status) and all(status is None for status in vaar_status):
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر1) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر1)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")
        else:
            return await event.client.send_message(event.chat_id, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر1) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر1)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")

    if len(var_status) == 0:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر1) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر1)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")
        else:
            return await event.client.send_message(event.chat_id, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر1) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر1)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")

    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    if not os.path.isdir(Config.TEMP_DIR):
        os.makedirs(Config.TEMP_DIR)

    sleeptimet = None
    try:
        sleeptimet = sleeptimem = int(input_str[0])
        addgvar("sec_spnasher", sleeptimet)
    except Exception:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر1` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر1 12 بالرد ع رسالة نصية او ميديا")
        else:
            return await event.client.send_message(event.chat_id, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر1` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر1 12 بالرد ع رسالة نصية او ميديا")

    rep = input_str[1:] if input_str[1:] else None
    spam_message = str(rep) if rep else None

    zq_lo = event.client

    if event.reply_to_msg_id and reply.media:
        start = datetime.now()
        downloaded_file_name = await event.client.download_media(
            reply, Config.TEMP_DIR
        )
        r_caption = reply.text if reply.text else None
        delgvar("msg_spnasher")
        if r_caption:
            addgvar("msg_spnasher", r_caption)
        vinfo = None
        if downloaded_file_name.endswith((".webp")):
            resize_image(downloaded_file_name)
        try:
            start = datetime.now()
            vinfo = uploader.upload_file(downloaded_file_name)
        except Exception as exc:
            await event.client.send_message(BOTLOG_CHATID, "**✧ خطا : **" + str(exc))
            os.remove(downloaded_file_name)
        else:
            end = datetime.now()
            ms_two = (end - start).seconds
            os.remove(downloaded_file_name)
            addgvar("med_spnasher", vinfo)
            REP_IMG = gvarstatus("med_spnasher")
            if REP_IMG:
                REP = [x for x in REP_IMG.split()]
                PIC = random.choice(REP)
                await event.client.send_file(BOTLOG_CHATID, PIC, caption=r_caption)
    #elif spam_message is not None:
        #addgvar("msg_spnasher", spam_message)

    elif event.reply_to_msg_id and reply.text:
        addgvar("msg_spnasher", reply.text)

    else:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر1` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر1 12 بالرد ع رسالة نصية او ميديا")
        else:
            return await event.client.send_message(event.chat_id, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر1` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر1 12 بالرد ع رسالة نصية او ميديا")

    rsr = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
    rsr += f"\n<b>• تم بـدء النشـر (المكرر1) .. بنجـاح ✅ </b>"
    if reply.media:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n ميديـا 🏕️"
    else:
        rsr += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{reply.text}</code>"
    rsr += f"\n\n<b>• لـ عـرض المجموعـات :</b> ارسـل ( <code>.قائمة مكرر1</code> )"
    rsr += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
    rsr += f"\n<b>• بـ تأخيـر</b> {sleeptimet} <b>ثانيـه ⏳</b>"
    rsr += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.المكرر1</code> )"
    rsr += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف مكرر1</code> )"
    await event.client.send_message(event.chat_id, rsr, parse_mode="html", link_preview=False)
    addgvar("status_spnasher", True)
    if BOTLOG:
        rss = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
        rss += f"\n<b>• تم بـدء النشـر (المكرر1) .. بنجـاح ✅ </b>"
        if reply.text:
            rss += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{reply.text}</code>"
        rss += f"\n\n<b>• لـ عـرض المجموعـات :</b> ارسـل ( <code>.قائمة مكرر1</code> )"
        rss += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
        rss += f"\n<b>• بـ تأخيـر</b> {sleeptimet} <b>ثانيـه ⏳</b>"
        rss += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.المكرر1</code> )"
        rss += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف مكرر1</code> )"
        await event.client.send_message(
            BOTLOG_CHATID,
            rss,
            parse_mode="html",
            link_preview=False,
        )

    global z_spnasher
    r_spnasher = True
    #chat_id = addgvar("chat_spnasher", event.chat_id)
    await rr_spnasher()



# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="اضف مكرر1?(?: |$)(.*)")
async def add_blacklist_chat(event):
    result = 0
    new_value = None
    input_str = event.pattern_match.group(1)
    if not input_str and not event.is_group:
        return await edit_or_reply(event, "**✾╎عـذراً .. اوامـر مكـرر1 خـاصه بالمجموعـات فقـط**")
    if input_str and input_str.isdigit():
        if input_str.startswith("-100"):
            new_value = int(input_str)
        else:
            chat_id = f"-100{input_str}"
            new_value = int(chat_id)
    else:
        new_value = int(event.chat_id)
    try:
        chat = await event.client.get_entity(event.chat_id)
        # قائمة بأسماء المتغيرات
        spvariables = [f"SppSuper_Id{i}" for i in range(1, 21)]  # إنشاء قائمة من Z_AK1 إلى Z_AK20
        # تحقق من حالة كل متغير
        #var_status = []
        # تحقق من حالة كل متغير
        for var in spvariables:
            status = gvarstatus(var)
            if (status is not None) and (status not in var_status):
                var_status.append(status)
        if new_value in var_status:
            if BOTLOG:
                await event.client.send_message(BOTLOG_CHATID, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر1) 🎡**")
                return await event.delete()
            else:
                return await edit_or_reply(event, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر1) 🎡**")
        for var in spvariables:
            if gvarstatus(var) is None:
                # إذا كانت القيمة None، نقوم بإضافة القيمة الجديدة
                addgvar(var, new_value)
                #print(f"تم إضافة القيمة '{new_value}' إلى المتغير '{var}'.")
                if BOTLOG:
                    await event.client.send_message(BOTLOG_CHATID, f"**• تم اضافـة المجموعـة**  {get_display_name(chat)} **.. بنجـاح ☑️**\n**• لـ قائمـة ڪـروبـات النشـر (المكرر1) 🎡**")
                    await event.delete()
                else:
                    await edit_or_reply(event, f"**• تم اضافـة المجموعـة**  {get_display_name(chat)} **.. بنجـاح ☑️**\n**• لـ قائمـة ڪـروبـات النشـر (المكرر1) 🎡**")
                break
            else:
                var_value = int(gvarstatus(var))
                if var_value == new_value:
                    if BOTLOG:
                        await event.client.send_message(BOTLOG_CHATID, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر1) 🎡**")
                        await event.delete()
                    else:
                        await edit_or_reply(event, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر1) 🎡**")
                    break
                #print(f"المتغير '{var}' لديه قيمة: {gvarstatus(var)}.")
                result += 1
    except Exception as e:
        print(e)
    if result == 20 or result == 21:
        return await edit_or_reply(event, f"**• عـذراً .. عـزيـزي ✖️**\n**• لا تستطيع اضافة اكثر من 20 ڪـروب للنشـر (المكرر1)**")


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="حذف مكرر1?(?: |$)(.*)")
async def add_blacklist_chat(event):
    input_str = event.pattern_match.group(1)
    chat_id = event.chat_id
    result = ""
    input_str = event.pattern_match.group(1)
    if not input_str and not event.is_group:
        return await edit_or_reply(event, "**✾╎عـذراً .. اوامـر مكـرر1 خـاصه بالمجموعـات فقـط**")
    if input_str and input_str.isdigit():
        if input_str.startswith("-100"):
            chat_id = int(input_str)
        else:
            chat_id = f"-100{input_str}"
            chat_id = int(chat_id)
    else:
        chat_id = int(event.chat_id)
    try:
        #chat = await event.client.get_entity(event.chat_id)
        # قائمة بأسماء المتغيرات
        spvariables = [f"SppSuper_Id{i}" for i in range(1, 21)]  # إنشاء قائمة من Z_AK1 إلى Z_AK20
        # تحقق من حالة كل متغير
        for var in spvariables:
            if gvarstatus(var) is not None:
                id_var = int(gvarstatus(var))
                if id_var == chat_id:
                    # إذا كانت القيمة None، نقوم بإضافة القيمة الجديدة
                    delgvar(var)
                    var_status.remove(id_var)
                    #print(f"تم إضافة القيمة '{new_value}' إلى المتغير '{var}'.")
                    await edit_or_reply(event, f"**• تم حذف المجموعـة.. بنجـاح ☑️**\n**• من قائمـة ڪـروبـات النشـر (المكرر1) 🎡**")
                    break
            else:
                #print(f"المتغير '{var}' لديه قيمة: {gvarstatus(var)}.")
                result += 1
    except Exception as e:
        print(e)
    if result == 20 or result == 21:
        return 


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="(قائمة مكرر1|قائمه مكرر1)$")
async def superlist_chat(event):
    # قائمة لتخزين حالة المتغيرات
    #var_status = []
    # تحقق من حالة كل متغير
    for var in sp_variables:
        status = gvarstatus(var)
        if (status is not None) and (status not in var_status):
            var_status.append(status)

    if len(var_status) == 0:
        return await edit_delete(
            event, "**- لا يوجـد كروبـات بعـد فـي قائمـة مكـرر1 ؟؟**"
        )
    result = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 **1قائمـة ڪـࢪوبـات مكـࢪࢪ**\n**⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆**\n"
    for chaat in var_status:
        chaat = int(chaat)
        chat = await get_chatinfo(chaat)
        chat_obj_info = await event.client.get_entity(chat.full_chat.id)
        chat_title = chat_obj_info.title
        result += f"• {chat_title}\n"
    await edit_or_reply(event, result)


@zq_lo.rep_cmd(pattern="(حذف قائمة مكرر1|حذف قائمه مكرر1)$")
async def delsuperlist_chat(event):
    spvariables = [f"SppSuper_Id{i}" for i in range(1, 21)]
    # تحقق من حالة كل متغير اذا كان موجود
    for var in spvariables:
        if gvarstatus(var) is not None:
            delgvar(var)
    var_status.clear()
    return await edit_or_reply(event, "**✾ تم حذف جميع المجموعات المضافة لقائمـة مكـرر1 ☑️**")


@zq_lo.rep_cmd(pattern="ايقاف (مكرر1|المكرر1|مؤقت1|المؤقت1)")
async def stop_super(event):
    global r_spnasher
    r_spnasher = False
    if gvarstatus("status_spnasher") is not None:
        delgvar("status_spnasher")
        if gvarstatus("chat_spnasher") is not None:
            delgvar("chat_spnasher")
        if gvarstatus("sec_spnasher") is not None:
            delgvar("sec_spnasher")
        if gvarstatus("msg_spnasher") is not None:
            delgvar("msg_spnasher")
        if gvarstatus("med_spnasher") is not None:
            delgvar("med_spnasher")

    await event.edit("**- تم إيقاف النشر التلقائي (مكرر1) .. بنجاح ✅**")


@zq_lo.rep_cmd(pattern="(اوامر مكرر1|اوامر المكرر1)")
async def cmd_super(baqir):
    await edit_or_reply(baqir, BaqirSpsuper_cmd)
### قسم مكرر ###

async def rrr_sp2nasher(zq_lo, sleeptimet, message):  # نشر عبر يوزرات المجموعات المخزنه
    media_sp2nasher = gvarstatus("med_sp2nasher") if gvarstatus("med_sp2nasher") else None
    msg_sp2nasher = gvarstatus("msg_sp2nasher") if gvarstatus("msg_sp2nasher") else None
    # تحقق من حالة كل متغير
    for var in sp2_variables:
        status = gvarstatus(var)
        if (status is not None) and (status not in var2_status):
            var2_status.append(status)

    global r_sp2nasher
    r_sp2nasher = True
    while r_sp2nasher:
        if gvarstatus("status_sp2nasher") is None:
            break
        for chat_iid in var2_status:
            if gvarstatus("status_sp2nasher") is None:
                break
            try:
                # Introduce random delays between 1 and sleeptimet seconds.
                # • التأخيرات العشوائية:
                # تقدم تأخيرات عشوائية بين إرسال الرسائل إلى مجموعات مختلفة.
                # وهذا يجعل نمط الإرسال أقل تجانسًا.
                await asyncio.sleep(random.uniform(2, 10))
                #await asyncio.sleep(random.uniform(1, sleeptimet))  # تعني الأعداد الأصغر (أسرع إرسالًا) (ولكن مخاطرة أعلى للحظر)
                
                #chat_iiid = chat_iid if chat_iid.startswith("-100") else f"-100{chat_iid}" 
                #chat = await zq_lo.get_entity(chat_iiid)
                ch_id = int(chat_iid)
                if media_sp2nasher is not None:
                    REP_IMG = gvarstatus("med_sp2nasher")
                    REP = [x for x in REP_IMG.split()]
                    PIC = random.choice(REP)
                    msg_sp2caption = gvarstatus("msg_sp2nasher") if gvarstatus("msg_sp2nasher") else ""
                    await zq_lo.send_file(ch_id, PIC, caption=msg_sp2caption)
                else:
                    await zq_lo.send_message(ch_id, msg_sp2nasher, link_preview=False)
                
                # Add a delay after each successful message send
                # يقوم بتقديم تأخير بعد كل رسالة ناجحة، مما يقلل بشكل أكبر من اندفاع النشاط
                await asyncio.sleep(random.uniform(11, 20)) # اضبط هذا النطاق بناءً على ملاحظاتك.
            
            except Exception as e:
                #print(f"drrr(143): Error in sending message to chat {chat.id}: {e}")
                # Consider adding more sophisticated error handling, like retry mechanisms
                #await asyncio.sleep(random.uniform(30, 60)) #Longer delay for errors
                #await asyncio.sleep(random.uniform(5, 10)) #Longer delay for errors
                #await zq_lo.send_message(BOTLOG_CHATID, f"**⌔ لا يمكن العثور على المجموعة أو الدردشة** {chat_iiid} :\n`{str(e)}`")
                pass
        
        # Wait for the specified sleeptimet before starting the next round
        await asyncio.sleep(sleeptimet)


async def rrr_sp2nasher():
    sleeptimet = int(gvarstatus("sec_sp2nasher"))
    message = gvarstatus("msg_sp2nasher")
    await rrr_sp2nasher(zq_lo, sleeptimet, message)


@zq_lo.rep_cmd(pattern=f"{SP2AM} ([\\s\\S]*)")
async def sp2ammer(event):
    if gvarstatus("status_sp2nasher"):
        if BOTLOG:
            await event.delete()
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية (مكرر2) سابقـه مفعله**\n**✧ ارسـل** ( `.اوامر مكرر3` ) ** لـ عرض اوامـر اضافيه لـ المكـرر3**")
        else:
            return await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية (مكرر2) سابقـه مفعله**\n**✧ ارسـل** ( `.اوامر مكرر3` ) ** لـ عرض اوامـر اضافيه لـ المكـرر3**")

    if not event.reply_to_msg_id:
        await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ ارسـل الامـر بالـرد ع الرسالة المراد نشرها**")
        return

    await event.delete()
    #input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)

    # قائمة بأسماء المتغيرات
    spvariables = [f"Spp2Super_Id{i}" for i in range(1, 21)] 
    # تحقق من حالة المتغيرات
    vaar_status = [gvarstatus(var) for var in spvariables]
    # تحقق من الشروط المطلوبة
    #if all(var2_status[0:2]) and all(status is None for status in var2_status[2:]):
    if all(vaar_status) and all(status is None for status in vaar_status):
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر2) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر2)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")
        else:
            return await event.client.send_message(event.chat_id, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر2) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر2)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")

    if len(var2_status) == 0:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر2) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر2)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")
        else:
            return await event.client.send_message(event.chat_id, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر2) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر2)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")

    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    if not os.path.isdir(Config.TEMP_DIR):
        os.makedirs(Config.TEMP_DIR)

    sleeptimet = None
    try:
        sleeptimet = sleeptimem = int(input_str[0])
        addgvar("sec_sp2nasher", sleeptimet)
    except Exception:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر2` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر2 12 بالرد ع رسالة نصية او ميديا")
        else:
            return await event.client.send_message(event.chat_id, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر2` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر2 12 بالرد ع رسالة نصية او ميديا")

    rep = input_str[1:] if input_str[1:] else None
    spam_message = str(rep) if rep else None

    zq_lo = event.client

    if event.reply_to_msg_id and reply.media:
        start = datetime.now()
        downloaded_file_name = await event.client.download_media(
            reply, Config.TEMP_DIR
        )
        r_caption = reply.text if reply.text else None
        delgvar("msg_sp2nasher")
        if r_caption:
            addgvar("msg_sp2nasher", r_caption)
        vinfo = None
        if downloaded_file_name.endswith((".webp")):
            resize_image(downloaded_file_name)
        try:
            start = datetime.now()
            vinfo = uploader.upload_file(downloaded_file_name)
        except Exception as exc:
            await event.client.send_message(BOTLOG_CHATID, "**✧ خطا : **" + str(exc))
            os.remove(downloaded_file_name)
        else:
            end = datetime.now()
            ms_two = (end - start).seconds
            os.remove(downloaded_file_name)
            addgvar("med_sp2nasher", vinfo)
            REP_IMG = gvarstatus("med_sp2nasher")
            if REP_IMG:
                REP = [x for x in REP_IMG.split()]
                PIC = random.choice(REP)
                await event.client.send_file(BOTLOG_CHATID, PIC, caption=r_caption)
    #elif spam_message is not None:
        #addgvar("msg_sp2nasher", spam_message)

    elif event.reply_to_msg_id and reply.text:
        addgvar("msg_sp2nasher", reply.text)

    else:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر2` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر2 12 بالرد ع رسالة نصية او ميديا")
        else:
            return await event.client.send_message(event.chat_id, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر2` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر2 12 بالرد ع رسالة نصية او ميديا")

    rsr = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
    rsr += f"\n<b>• تم بـدء النشـر (المكرر2) .. بنجـاح ✅ </b>"
    if reply.media:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n ميديـا 🏕️"
    else:
        rsr += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{reply.text}</code>"
    rsr += f"\n\n<b>• لـ عـرض المجموعـات :</b> ارسـل ( <code>.قائمة مكرر2</code> )"
    rsr += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
    rsr += f"\n<b>• بـ تأخيـر</b> {sleeptimet} <b>ثانيـه ⏳</b>"
    rsr += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.المكرر2</code> )"
    rsr += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف مكرر2</code> )"
    await event.client.send_message(event.chat_id, rsr, parse_mode="html", link_preview=False)
    addgvar("status_sp2nasher", True)
    if BOTLOG:
        rss = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
        rss += f"\n<b>• تم بـدء النشـر (المكرر2) .. بنجـاح ✅ </b>"
        if reply.text:
            rss += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{reply.text}</code>"
        rss += f"\n\n<b>• لـ عـرض المجموعـات :</b> ارسـل ( <code>.قائمة مكرر2</code> )"
        rss += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
        rss += f"\n<b>• بـ تأخيـر</b> {sleeptimet} <b>ثانيـه ⏳</b>"
        rss += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.المكرر2</code> )"
        rss += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف مكرر2</code> )"
        await event.client.send_message(
            BOTLOG_CHATID,
            rss,
            parse_mode="html",
            link_preview=False,
        )

    global r_sp2nasher
    r_sp2nasher = True
    #chat_id = addgvar("chat_sp2nasher", event.chat_id)
    await rr_sp2nasher()



# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="اضف مكرر2?(?: |$)(.*)")
async def add2_blacklist_chat(event):
    result = 0
    new_value = None
    input_str = event.pattern_match.group(1)
    if not input_str and not event.is_group:
        return await edit_or_reply(event, "**✾╎عـذراً .. اوامـر مكـرر2 خـاصه بالمجموعـات فقـط**")
    if input_str and input_str.isdigit():
        if input_str.startswith("-100"):
            new_value = int(input_str)
        else:
            chat_id = f"-100{input_str}"
            new_value = int(chat_id)
    else:
        new_value = int(event.chat_id)
    try:
        chat = await event.client.get_entity(event.chat_id)
        # قائمة بأسماء المتغيرات
        spvariables = [f"Spp2Super_Id{i}" for i in range(1, 21)]  # إنشاء قائمة من Z_AK1 إلى Z_AK20
        # تحقق من حالة كل متغير
        #var2_status = []
        # تحقق من حالة كل متغير
        for var in spvariables:
            status = gvarstatus(var)
            if (status is not None) and (status not in var2_status):
                var2_status.append(status)
        if new_value in var2_status:
            if BOTLOG:
                await event.client.send_message(BOTLOG_CHATID, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر2) 🎡**")
                return await event.delete()
            else:
                return await edit_or_reply(event, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر2) 🎡**")
        for var in spvariables:
            if gvarstatus(var) is None:
                # إذا كانت القيمة None، نقوم بإضافة القيمة الجديدة
                addgvar(var, new_value)
                #print(f"تم إضافة القيمة '{new_value}' إلى المتغير '{var}'.")
                if BOTLOG:
                    await event.client.send_message(BOTLOG_CHATID, f"**• تم اضافـة المجموعـة**  {get_display_name(chat)} **.. بنجـاح ☑️**\n**• لـ قائمـة ڪـروبـات النشـر (المكرر2) 🎡**")
                    await event.delete()
                else:
                    await edit_or_reply(event, f"**• تم اضافـة المجموعـة**  {get_display_name(chat)} **.. بنجـاح ☑️**\n**• لـ قائمـة ڪـروبـات النشـر (المكرر2) 🎡**")
                break
            else:
                var_value = int(gvarstatus(var))
                if var_value == new_value:
                    if BOTLOG:
                        await event.client.send_message(BOTLOG_CHATID, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر2) 🎡**")
                        await event.delete()
                    else:
                        await edit_or_reply(event, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر2) 🎡**")
                    break
                #print(f"المتغير '{var}' لديه قيمة: {gvarstatus(var)}.")
                result += 1
    except Exception as e:
        print(e)
    if result == 20 or result == 21:
        return await edit_or_reply(event, f"**• عـذراً .. عـزيـزي ✖️**\n**• لا تستطيع اضافة اكثر من 20 ڪـروب للنشـر (المكرر2)**")


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="حذف مكرر2?(?: |$)(.*)")
async def add2_blacklist_chat(event):
    input_str = event.pattern_match.group(1)
    chat_id = event.chat_id
    result = ""
    input_str = event.pattern_match.group(1)
    if not input_str and not event.is_group:
        return await edit_or_reply(event, "**✾╎عـذراً .. اوامـر مكـرر2 خـاصه بالمجموعـات فقـط**")
    if input_str and input_str.isdigit():
        if input_str.startswith("-100"):
            chat_id = int(input_str)
        else:
            chat_id = f"-100{input_str}"
            chat_id = int(chat_id)
    else:
        chat_id = int(event.chat_id)
    try:
        #chat = await event.client.get_entity(event.chat_id)
        # قائمة بأسماء المتغيرات
        spvariables = [f"Spp2Super_Id{i}" for i in range(1, 21)]  # إنشاء قائمة من Z_AK1 إلى Z_AK20
        # تحقق من حالة كل متغير
        for var in spvariables:
            if gvarstatus(var) is not None:
                id_var = int(gvarstatus(var))
                if id_var == chat_id:
                    # إذا كانت القيمة None، نقوم بإضافة القيمة الجديدة
                    delgvar(var)
                    var2_status.remove(id_var)
                    #print(f"تم إضافة القيمة '{new_value}' إلى المتغير '{var}'.")
                    await edit_or_reply(event, f"**• تم حذف المجموعـة.. بنجـاح ☑️**\n**• من قائمـة ڪـروبـات النشـر (المكرر2) 🎡**")
                    break
            else:
                #print(f"المتغير '{var}' لديه قيمة: {gvarstatus(var)}.")
                result += 1
    except Exception as e:
        print(e)
    if result == 20 or result == 21:
        return 


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="(قائمة مكرر2|قائمه مكرر2)$")
async def superlist2_chat(event):
    # قائمة لتخزين حالة المتغيرات
    #var2_status = []
    # تحقق من حالة كل متغير
    for var in sp2_variables:
        status = gvarstatus(var)
        if (status is not None) and (status not in var2_status):
            var2_status.append(status)

    if len(var2_status) == 0:
        return await edit_delete(
            event, "**- لا يوجـد كروبـات بعـد فـي قائمـة مكـرر2 ؟؟**"
        )
    result = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 **قائمـة ڪـࢪوبـات مكـࢪࢪ2**\n**⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆**\n"
    for chaat in var2_status:
        chaat = int(chaat)
        chat = await get_chatinfo(chaat)
        chat_obj_info = await event.client.get_entity(chat.full_chat.id)
        chat_title = chat_obj_info.title
        result += f"• {chat_title}\n"
    await edit_or_reply(event, result)


@zq_lo.rep_cmd(pattern="(حذف قائمة مكرر2|حذف قائمه مكرر2)$")
async def delsuperlist_chat(event):
    spvariables = [f"Spp2Super_Id{i}" for i in range(1, 21)]
    # تحقق من حالة كل متغير اذا كان موجود
    for var in spvariables:
        if gvarstatus(var) is not None:
            delgvar(var)
    var2_status.clear()
    return await edit_or_reply(event, "**✾ تم حذف جميع المجموعات المضافة لقائمـة مكـرر2 ☑️**")


@zq_lo.rep_cmd(pattern="ايقاف (مكرر2|المكرر2|مؤقت2|المؤقت2)")
async def stop2_super(event):
    global r_sp2nasher
    r_sp2nasher = False
    if gvarstatus("status_sp2nasher") is not None:
        delgvar("status_sp2nasher")
        if gvarstatus("chat_sp2nasher") is not None:
            delgvar("chat_sp2nasher")
        if gvarstatus("sec_sp2nasher") is not None:
            delgvar("sec_sp2nasher")
        if gvarstatus("msg_sp2nasher") is not None:
            delgvar("msg_sp2nasher")
        if gvarstatus("med_sp2nasher") is not None:
            delgvar("med_sp2nasher")

    await event.edit("**- تم إيقاف النشر التلقائي (مكرر2) .. بنجاح ✅**")


@zq_lo.rep_cmd(pattern="(اوامر مكرر2|اوامر المكرر2)")
async def cmd3_super(baqir):
    await edit_or_reply(baqir, BaqirSp2super_cmd)
### قسم مكرر2 ###


#### قسم اوامر مكرر3###
async def rrr_sp3nasher(zq_lo, sleeptimet, message):  # نشر عبر يوزرات المجموعات المخزنه
    media_sp3nasher = gvarstatus("med_sp3nasher") if gvarstatus("med_sp3nasher") else None
    msg_sp3nasher = gvarstatus("msg_sp3nasher") if gvarstatus("msg_sp3nasher") else None
    # تحقق من حالة كل متغير
    for var in sp3_variables:
        status = gvarstatus(var)
        if (status is not None) and (status not in var3_status):
            var3_status.append(status)

    global r_sp3nasher
    r_sp3nasher = True
    while r_sp3nasher:
        if gvarstatus("status_sp3nasher") is None:
            break
        for chat_iid in var3_status:
            if gvarstatus("status_sp3nasher") is None:
                break
            try:
                # Introduce random delays between 1 and sleeptimet seconds.
                # • التأخيرات العشوائية:
                # تقدم تأخيرات عشوائية بين إرسال الرسائل إلى مجموعات مختلفة.
                # وهذا يجعل نمط الإرسال أقل تجانسًا.
                await asyncio.sleep(random.uniform(2, 10))
                #await asyncio.sleep(random.uniform(1, sleeptimet))  # تعني الأعداد الأصغر (أسرع إرسالًا) (ولكن مخاطرة أعلى للحظر)
                
                #chat_iiid = chat_iid if chat_iid.startswith("-100") else f"-100{chat_iid}" 
                #chat = await zq_lo.get_entity(chat_iiid)
                ch_id = int(chat_iid)
                if media_sp3nasher is not None:
                    REP_IMG = gvarstatus("med_sp3nasher")
                    REP = [x for x in REP_IMG.split()]
                    PIC = random.choice(REP)
                    msg_sp3caption = gvarstatus("msg_sp3nasher") if gvarstatus("msg_sp3nasher") else ""
                    await zq_lo.send_file(ch_id, PIC, caption=msg_sp3caption)
                else:
                    await zq_lo.send_message(ch_id, msg_sp3nasher, link_preview=False)
                
                # Add a delay after each successful message send
                # يقوم بتقديم تأخير بعد كل رسالة ناجحة، مما يقلل بشكل أكبر من اندفاع النشاط
                await asyncio.sleep(random.uniform(11, 20)) # اضبط هذا النطاق بناءً على ملاحظاتك.
            
            except Exception as e:
                #print(f"drrr(143): Error in sending message to chat {chat.id}: {e}")
                # Consider adding more sophisticated error handling, like retry mechanisms
                #await asyncio.sleep(random.uniform(30, 60)) #Longer delay for errors
                #await asyncio.sleep(random.uniform(5, 10)) #Longer delay for errors
                #await zq_lo.send_message(BOTLOG_CHATID, f"**⌔ لا يمكن العثور على المجموعة أو الدردشة** {chat_iiid} :\n`{str(e)}`")
                pass
        
        # Wait for the specified sleeptimet before starting the next round
        await asyncio.sleep(sleeptimet)


async def zz_sp3nasher():
    sleeptimet = int(gvarstatus("sec_sp3nasher"))
    message = gvarstatus("msg_sp3nasher")
    await rrr_sp3nasher(zq_lo, sleeptimet, message)


@zq_lo.rep_cmd(pattern=f"{SP3AM} ([\s\S]*)")
async def sp3ammer(event):
    if gvarstatus("status_sp3nasher"):
        if BOTLOG:
            await event.delete()
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية (مكرر3) سابقـه مفعله**\n**✧ ارسـل** ( `.اوامر مكرر2` ) او (`.اوامر مكرر`) ** لـ عرض اوامـر اضافيه لـ المكـرر**")
        else:
            return await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية (مكرر3) سابقـه مفعله**\n**✧ ارسـل** ( `.اوامر مكرر2` ) او (`.اوامر مكرر`) ** لـ عرض اوامـر اضافيه لـ المكـرر**")

    if not event.reply_to_msg_id:
        await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ ارسـل الامـر بالـرد ع الرسالة المراد نشرها**")
        return

    await event.delete()
    #input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)

    # قائمة بأسماء المتغيرات
    spvariables = [f"Spp3Super_Id{i}" for i in range(1, 21)] 
    # تحقق من حالة المتغيرات
    vaar_status = [gvarstatus(var) for var in spvariables]
    # تحقق من الشروط المطلوبة
    #if all(var3_status[0:2]) and all(status is None for status in var3_status[2:]):
    if all(vaar_status) and all(status is None for status in vaar_status):
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر3) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر3)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")
        else:
            return await event.client.send_message(event.chat_id, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر3) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر3)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")

    if len(var3_status) == 0:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر3) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر3)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")
        else:
            return await event.client.send_message(event.chat_id, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد مجموعات مضافه لقائمـة (مكرر3) ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف مكرر3)\n**✧ وهكذا قم بتكرار الامر لبقية المجموعات**")

    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    if not os.path.isdir(Config.TEMP_DIR):
        os.makedirs(Config.TEMP_DIR)

    sleeptimet = None
    try:
        sleeptimet = sleeptimem = int(input_str[0])
        addgvar("sec_sp3nasher", sleeptimet)
    except Exception:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر3` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر3 12 بالرد ع رسالة نصية او ميديا")
        else:
            return await event.client.send_message(event.chat_id, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر3` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر3 12 بالرد ع رسالة نصية او ميديا")

    rep = input_str[1:] if input_str[1:] else None
    spam_message = str(rep) if rep else None

    zq_lo = event.client

    if event.reply_to_msg_id and reply.media:
        start = datetime.now()
        downloaded_file_name = await event.client.download_media(
            reply, Config.TEMP_DIR
        )
        r_caption = reply.text if reply.text else None
        delgvar("msg_sp3nasher")
        if r_caption:
            addgvar("msg_sp3nasher", r_caption)
        vinfo = None
        if downloaded_file_name.endswith((".webp")):
            resize_image(downloaded_file_name)
        try:
            start = datetime.now()
            vinfo = uploader.upload_file(downloaded_file_name)
        except Exception as exc:
            await event.client.send_message(BOTLOG_CHATID, "**✧ خطا : **" + str(exc))
            os.remove(downloaded_file_name)
        else:
            end = datetime.now()
            ms_two = (end - start).seconds
            os.remove(downloaded_file_name)
            addgvar("med_sp3nasher", vinfo)
            REP_IMG = gvarstatus("med_sp3nasher")
            if REP_IMG:
                REP = [x for x in REP_IMG.split()]
                PIC = random.choice(REP)
                await event.client.send_file(BOTLOG_CHATID, PIC, caption=r_caption)
    #elif spam_message is not None:
        #addgvar("msg_sp3nasher", spam_message)

    elif event.reply_to_msg_id and reply.text:
        addgvar("msg_sp3nasher", reply.text)

    else:
        if BOTLOG:
            return await event.client.send_message(BOTLOG_CHATID, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر3` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر3 12 بالرد ع رسالة نصية او ميديا")
        else:
            return await event.client.send_message(event.chat_id, "**- ارسـل الامـر بالشكـل التالي:**\n\n`.مكرر3` **+ عدد ثواني تأخير التكرار (بالرد ع نص او ميديا)**\n**- مثـال :**\n.مكرر3 12 بالرد ع رسالة نصية او ميديا")

    rsr = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
    rsr += f"\n<b>• تم بـدء النشـر (المكرر3) .. بنجـاح ✅ </b>"
    if reply.media:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n ميديـا 🏕️"
    else:
        rsr += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{reply.text}</code>"
    rsr += f"\n\n<b>• لـ عـرض المجموعـات :</b> ارسـل ( <code>.قائمة مكرر3</code> )"
    rsr += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
    rsr += f"\n<b>• بـ تأخيـر</b> {sleeptimet} <b>ثانيـه ⏳</b>"
    rsr += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.المكرر3</code> )"
    rsr += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف مكرر3</code> )"
    await event.client.send_message(event.chat_id, rsr, parse_mode="html", link_preview=False)
    addgvar("status_sp3nasher", True)
    if BOTLOG:
        rss = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
        rss += f"\n<b>• تم بـدء النشـر (المكرر3) .. بنجـاح ✅ </b>"
        if reply.text:
            rss += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{reply.text}</code>"
        rss += f"\n\n<b>• لـ عـرض المجموعـات :</b> ارسـل ( <code>.قائمة مكرر3</code> )"
        rss += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
        rss += f"\n<b>• بـ تأخيـر</b> {sleeptimet} <b>ثانيـه ⏳</b>"
        rss += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.المكرر3</code> )"
        rss += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف مكرر3</code> )"
        await event.client.send_message(
            BOTLOG_CHATID,
            rss,
            parse_mode="html",
            link_preview=False,
        )

    global r_sp3nasher
    r_sp3nasher = True
    #chat_id = addgvar("chat_sp3nasher", event.chat_id)
    await rr_sp3nasher()


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="اضف مكرر3?(?: |$)(.*)")
async def add3_blacklist_chat(event):
    result = 0
    new_value = None
    input_str = event.pattern_match.group(1)
    if not input_str and not event.is_group:
        return await edit_or_reply(event, "**✾╎عـذراً .. اوامـر مكـرر3 خـاصه بالمجموعـات فقـط**")
    if input_str and input_str.isdigit():
        if input_str.startswith("-100"):
            new_value = int(input_str)
        else:
            chat_id = f"-100{input_str}"
            new_value = int(chat_id)
    else:
        new_value = int(event.chat_id)
    try:
        chat = await event.client.get_entity(event.chat_id)
        # قائمة بأسماء المتغيرات
        spvariables = [f"Spp3Super_Id{i}" for i in range(1, 21)]  # إنشاء قائمة من Z_AK1 إلى Z_AK20
        # تحقق من حالة كل متغير
        #var3_status = []
        # تحقق من حالة كل متغير
        for var in spvariables:
            status = gvarstatus(var)
            if (status is not None) and (status not in var3_status):
                var3_status.append(status)
        if new_value in var3_status:
            if BOTLOG:
                await event.client.send_message(BOTLOG_CHATID, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر3) 🎡**")
                return await event.delete()
            else:
                return await edit_or_reply(event, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر3) 🎡**")
        for var in spvariables:
            if gvarstatus(var) is None:
                # إذا كانت القيمة None، نقوم بإضافة القيمة الجديدة
                addgvar(var, new_value)
                #print(f"تم إضافة القيمة '{new_value}' إلى المتغير '{var}'.")
                if BOTLOG:
                    await event.client.send_message(BOTLOG_CHATID, f"**• تم اضافـة المجموعـة**  {get_display_name(chat)} **.. بنجـاح ☑️**\n**• لـ قائمـة ڪـروبـات النشـر (المكرر3) 🎡**")
                    await event.delete()
                else:
                    await edit_or_reply(event, f"**• تم اضافـة المجموعـة**  {get_display_name(chat)} **.. بنجـاح ☑️**\n**• لـ قائمـة ڪـروبـات النشـر (المكرر3) 🎡**")
                break
            else:
                var_value = int(gvarstatus(var))
                if var_value == new_value:
                    if BOTLOG:
                        await event.client.send_message(BOTLOG_CHATID, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر3) 🎡**")
                        await event.delete()
                    else:
                        await edit_or_reply(event, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر (المكرر3) 🎡**")
                    break
                #print(f"المتغير '{var}' لديه قيمة: {gvarstatus(var)}.")
                result += 1
    except Exception as e:
        print(e)
    if result == 20 or result == 21:
        return await edit_or_reply(event, f"**• عـذراً .. عـزيـزي ✖️**\n**• لا تستطيع اضافة اكثر من 20 ڪـروب للنشـر (المكرر3)**")


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="حذف مكرر3?(?: |$)(.*)")
async def add3_blacklist_chat(event):
    input_str = event.pattern_match.group(1)
    chat_id = event.chat_id
    result = ""
    input_str = event.pattern_match.group(1)
    if not input_str and not event.is_group:
        return await edit_or_reply(event, "**✾╎عـذراً .. اوامـر مكـرر3 خـاصه بالمجموعـات فقـط**")
    if input_str and input_str.isdigit():
        if input_str.startswith("-100"):
            chat_id = int(input_str)
        else:
            chat_id = f"-100{input_str}"
            chat_id = int(chat_id)
    else:
        chat_id = int(event.chat_id)
    try:
        #chat = await event.client.get_entity(event.chat_id)
        # قائمة بأسماء المتغيرات
        spvariables = [f"Spp3Super_Id{i}" for i in range(1, 21)]  # إنشاء قائمة من Z_AK1 إلى Z_AK20
        # تحقق من حالة كل متغير
        for var in spvariables:
            if gvarstatus(var) is not None:
                id_var = int(gvarstatus(var))
                if id_var == chat_id:
                    # إذا كانت القيمة None، نقوم بإضافة القيمة الجديدة
                    delgvar(var)
                    var3_status.remove(id_var)
                    #print(f"تم إضافة القيمة '{new_value}' إلى المتغير '{var}'.")
                    await edit_or_reply(event, f"**• تم حذف المجموعـة.. بنجـاح ☑️**\n**• من قائمـة ڪـروبـات النشـر (المكرر3) 🎡**")
                    break
            else:
                #print(f"المتغير '{var}' لديه قيمة: {gvarstatus(var)}.")
                result += 1
    except Exception as e:
        print(e)
    if result == 20 or result == 21:
        return 


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="(قائمة مكرر3|قائمه مكرر3)$")
async def superlist3_chat(event):
    # قائمة لتخزين حالة المتغيرات
    #var3_status = []
    # تحقق من حالة كل متغير
    for var in sp3_variables:
        status = gvarstatus(var)
        if (status is not None) and (status not in var3_status):
            var3_status.append(status)

    if len(var3_status) == 0:
        return await edit_delete(
            event, "**- لا يوجـد كروبـات بعـد فـي قائمـة مكـرر3 ؟؟**"
        )
    result = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 **قائمـة ڪـࢪوبـات مكـࢪࢪ3**\n**⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆**\n"
    for chaat in var3_status:
        chaat = int(chaat)
        chat = await get_chatinfo(chaat)
        chat_obj_info = await event.client.get_entity(chat.full_chat.id)
        chat_title = chat_obj_info.title
        result += f"• {chat_title}\n"
    await edit_or_reply(event, result)


@zq_lo.rep_cmd(pattern="(حذف قائمة مكرر3|حذف قائمه مكرر3)$")
async def delsuperlist3_chat(event):
    spvariables = [f"Spp3Super_Id{i}" for i in range(1, 21)]
    # تحقق من حالة كل متغير اذا كان موجود
    for var in spvariables:
        if gvarstatus(var) is not None:
            delgvar(var)
    var3_status.clear()
    return await edit_or_reply(event, "**✾ تم حذف جميع المجموعات المضافة لقائمـة مكـرر3 ☑️**")


@zq_lo.rep_cmd(pattern="ايقاف (مكرر3|المكرر3|مؤقت3|المؤقت3)")
async def stop3_super(event):
    global r_sp3nasher
    r_sp3nasher = False
    if gvarstatus("status_sp3nasher") is not None:
        delgvar("status_sp3nasher")
        if gvarstatus("chat_sp3nasher") is not None:
            delgvar("chat_sp3nasher")
        if gvarstatus("sec_sp3nasher") is not None:
            delgvar("sec_sp3nasher")
        if gvarstatus("msg_sp3nasher") is not None:
            delgvar("msg_sp3nasher")
        if gvarstatus("med_sp3nasher") is not None:
            delgvar("med_sp3nasher")

    await event.edit("**- تم إيقاف النشر التلقائي (مكرر3) .. بنجاح ✅**")


@zq_lo.rep_cmd(pattern="(اوامر مكرر3|اوامر المكرر3)")
async def cmd3_super(baqir):
    await edit_or_reply(baqir, BaqirSp3super_cmd)
### قسم مكرر3 ###


async def rrr_nasher(zq_lo, sleeptimet, message):  # نشر عبر يوزرات المجموعات المخزنه
    # قائمة لتخزين حالة المتغيرات
    var_status = []
    # تحقق من حالة كل متغير
    for var in su_variables:
        status = gvarstatus(var)
        if status is not None:
            var_status.append(status)
    global r_super
    r_super = True
    while r_super:
        for chat_iid in var_status:
            try:
                # Introduce random delays between 1 and sleeptimet seconds.
                # • التأخيرات العشوائية:
                # تقدم تأخيرات عشوائية بين إرسال الرسائل إلى مجموعات مختلفة.
                # وهذا يجعل نمط الإرسال أقل تجانسًا.
                await asyncio.sleep(random.uniform(2, 10))
                #await asyncio.sleep(random.uniform(1, sleeptimet))  # تعني الأعداد الأصغر (أسرع إرسالًا) (ولكن مخاطرة أعلى للحظر)
                
                #chat_iiid = chat_iid if chat_iid.startswith("-100") else f"-100{chat_iid}" 
                #chat = await zq_lo.get_entity(chat_iiid)
                ch_id = int(chat_iid)
                if gvarstatus("med_nasher") is not None:
                    REP_IMG = gvarstatus("med_nasher")
                    REP = [x for x in REP_IMG.split()]
                    PIC = random.choice(REP)
                    msg_caption = gvarstatus("msg_nasher") if gvarstatus("msg_nasher") else ""
                    await zq_lo.send_file(ch_id, PIC, caption=msg_caption)
                else:
                    msg_nasher = gvarstatus("msg_nasher")
                    await zq_lo.send_message(ch_id, msg_nasher, link_preview=False)
                
                # Add a delay after each successful message send
                # يقوم بتقديم تأخير بعد كل رسالة ناجحة، مما يقلل بشكل أكبر من اندفاع النشاط
                await asyncio.sleep(random.uniform(11, 20)) # اضبط هذا النطاق بناءً على ملاحظاتك.
            
            except Exception as e:
                #print(f"drrr(143): Error in sending message to chat {chat.id}: {e}")
                # Consider adding more sophisticated error handling, like retry mechanisms
                #await asyncio.sleep(random.uniform(30, 60)) #Longer delay for errors
                #await asyncio.sleep(random.uniform(5, 10)) #Longer delay for errors
                #await zedub.send_message(BOTLOG_CHATID, f"**⌔ لا يمكن العثور على المجموعة أو الدردشة** {chat_iiid} :\n`{str(e)}`")
                pass
        
        # Wait for the specified sleeptimet before starting the next round
        await asyncio.sleep(sleeptimet)


async def zz_nasher():
    sleeptimet = int(gvarstatus("sec_nasher"))
    message = gvarstatus("msg_nasher")
    await rrr_nasher(zq_lo, sleeptimet, message)


# ينشر لمجموعات محددة فقط بالامر
@zq_lo.rep_cmd(pattern="نشر")
async def _(event): # .نشر + عدد الثواني الفاصله + يوزرات المجموعات بالرد ع الرسالة
    if gvarstatus("status_nasher") or gvarstatus("status_allnasher") or gvarstatus("status_nsuper") or gvarstatus("status_spnasher"):
        return await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية نشر سابقـه مفعله**\n**✧ ارسـل** ( `.ايقاف النشر` ) ** لـ إيقافها اولاً**")
    if not event.reply_to_msg_id:
        await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ ارسـل الامـر بالـرد ع الرسالة المراد نشرها**")
        return
    await event.delete()
    #input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)

    # قائمة بأسماء المتغيرات
    variables = [f"Super_Id{i}" for i in range(1, 21)] 
    # تحقق من حالة المتغيرات
    var_status = [gvarstatus(var) for var in variables]
    # تحقق من الشروط المطلوبة
    if all(var_status[0:2]) and all(status is None for status in var_status[2:]):
        return await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي**\n**✧ لايوجد سوبرات مضافه لقائمـة النشر ؟!**\n**✧ قم بالذهاب اولاً لمجموعات السوبر التي تريد النشر فيها**\n**✧ ثم ارسل الامر** (.اضف سوبر)\n**✧ وهكذا قم بتكرار الامر لبقية السوبرات**")

    parameters = re.split(r'\s+', event.text.strip(), maxsplit=2)
    #if len(parameters) != 2:
        #return await edit_or_reply(event, "**- امـر خاطـىء .. ارسـل ( .النشر ) لـ تصفح اوامـر النشـر التلقائي**")
    #rrr = await edit_or_reply(event, "**✧ جـاري بـدء النشـر في المجموعـات ...الرجـاء الانتظـار**")
    if not os.path.isdir(Config.TEMP_DIR):
        os.makedirs(Config.TEMP_DIR)
    seconds = int(parameters[1])
    #chat_usernames = parameters[2].split()
    #seconds = int(input_str[0])
    #chat_usernames = input_str[1:]
    #chat_usernames_str = " ".join(chat_usernames)
    #print(chat_usernames_str)
    addgvar("sec_nasher", seconds)
    #addgvar("chat_nasher", chat_usernames_str)
    zq_lo = event.client
    global r_super
    r_super = True
    message = await event.get_reply_message()
    if message.media:
        start = datetime.now()
        downloaded_file_name = await event.client.download_media(
            message, Config.TEMP_DIR
        )
        r_caption = message.text if message.text else None
        delgvar("msg_nasher")
        if r_caption:
            addgvar("msg_nasher", r_caption)
        vinfo = None
        if downloaded_file_name.endswith((".webp")):
            resize_image(downloaded_file_name)
        try:
            start = datetime.now()
            vinfo = uploader.upload_file(downloaded_file_name)
        except Exception as exc:
            await event.client.send_message(BOTLOG_CHATID, "**✧ خطا : **" + str(exc))
            os.remove(downloaded_file_name)
        else:
            end = datetime.now()
            ms_two = (end - start).seconds
            os.remove(downloaded_file_name)
            addgvar("med_nasher", vinfo)
            REP_IMG = gvarstatus("med_nasher")
            if REP_IMG:
                REP = [x for x in REP_IMG.split()]
                PIC = random.choice(REP)
                await event.client.send_file(BOTLOG_CHATID, PIC, caption=r_caption)
    elif message.text:
        addgvar("msg_nasher", message.text)
    else:
        return
    rsr = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
    rsr += f"\n<b>• تمت بـدء النشـر .. بنجـاح ✅ </b>"
    if message.media:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n ميديـا 🏕️"
    else:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n نـص 📝"
    rsr += f"\n<b>• المجموعـات :</b> ارسـل (.السوبرات)"
    rsr += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
    rsr += f"\n<b>• بـ تأخيـر</b> {seconds} <b>ثانيـه ⏳</b>"
    rsr += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.النشر</code> )"
    rsr += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف النشر</code> )"
    await event.client.send_message(event.chat_id, rsr, parse_mode="html", link_preview=False)
    addgvar("status_nasher", True)
    if BOTLOG:
        rss = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
        rss += f"\n<b>• تمت بـدء النشـر .. بنجـاح ✅ </b>"
        if message.text:
            rss += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{message.text}</code>"
        rss += f"\n<b>• المجموعـات :</b> ارسـل (.السوبرات)"
        rss += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
        rss += f"\n<b>• بـ تأخيـر</b> {seconds} <b>ثانيـه ⏳</b>"
        rss += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.النشر</code> )"
        rss += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف النشر</code> )"
        await event.client.send_message(
            BOTLOG_CHATID,
            rss,
            parse_mode="html",
            link_preview=False,
        )
    await rr_nasher()



# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="اضف سوبر?(?: |$)(.*)")
async def add_blacklist_chat(event):
    result = 0
    new_value = None
    input_str = event.pattern_match.group(1)
    if not input_str and not event.is_group:
        return await edit_or_reply(event, "**✾╎عـذراً .. اوامـر السوبـر خـاصه بالمجموعـات فقـط**")
    if input_str and input_str.isdigit():
        if input_str.startswith("-100"):
            new_value = int(input_str)
        else:
            chat_id = f"-100{input_str}"
            new_value = int(chat_id)
    else:
        new_value = int(event.chat_id)
    try:
        chat = await event.client.get_entity(event.chat_id)
        # قائمة بأسماء المتغيرات
        variables = [f"Super_Id{i}" for i in range(1, 21)]  # إنشاء قائمة من Z_AK1 إلى Z_AK20
        # تحقق من حالة كل متغير
        var_status = []
        # تحقق من حالة كل متغير
        for var in variables:
            status = gvarstatus(var)
            if status is not None:
                var_status.append(status)
        if new_value in var_status:
            if BOTLOG:
                await event.client.send_message(BOTLOG_CHATID, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر 🎡**")
                return await event.delete()
            else:
                return await edit_or_reply(event, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر 🎡**")
        for var in variables:
            if gvarstatus(var) is None:
                # إذا كانت القيمة None، نقوم بإضافة القيمة الجديدة
                addgvar(var, new_value)
                #print(f"تم إضافة القيمة '{new_value}' إلى المتغير '{var}'.")
                if BOTLOG:
                    await event.client.send_message(BOTLOG_CHATID, f"**• تم اضافـة المجموعـة**  {get_display_name(chat)} **.. بنجـاح ☑️**\n**• لـ قائمـة ڪـروبـات النشـر 🎡**")
                    await event.delete()
                else:
                    await edit_or_reply(event, f"**• تم اضافـة المجموعـة**  {get_display_name(chat)} **.. بنجـاح ☑️**\n**• لـ قائمـة ڪـروبـات النشـر 🎡**")
                break
            else:
                var_value = int(gvarstatus(var))
                if var_value == new_value:
                    if BOTLOG:
                        await event.client.send_message(BOTLOG_CHATID, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر 🎡**")
                        await event.delete()
                    else:
                        await edit_or_reply(event, f"**• المجموعـة**  {get_display_name(chat)} **.. ☑️**\n**• مضافه مسبقاً لـ قائمـة ڪـروبـات النشـر 🎡**")
                    break
                #print(f"المتغير '{var}' لديه قيمة: {gvarstatus(var)}.")
                result += 1
    except Exception as e:
        print(e)
    if result == 20 or result == 21:
        return await edit_or_reply(event, f"**• عـذراً .. عـزيـزي ✖️**\n**• لا تستطيع اضافة اكثر من 20 ڪـروب للنشـر**")


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="حذف سوبر?(?: |$)(.*)")
async def add_blacklist_chat(event):
    input_str = event.pattern_match.group(1)
    chat_id = event.chat_id
    result = ""
    input_str = event.pattern_match.group(1)
    if not event.is_group:
        return await edit_or_reply(event, "**✾╎عـذراً .. اوامـر السوبـر خـاصه بالمجموعـات فقـط**")
    if input_str and input_str.isdigit():
        if input_str.startswith("-100"):
            chat_id = int(input_str)
        else:
            chat_id = f"-100{input_str}"
            chat_id = int(chat_id)
    else:
        chat_id = int(event.chat_id)
    try:
        #chat = await event.client.get_entity(event.chat_id)
        # قائمة بأسماء المتغيرات
        variables = [f"Super_Id{i}" for i in range(1, 21)]  # إنشاء قائمة من R_AK1 إلى R_AK20
        # تحقق من حالة كل متغير
        for var in variables:
            if gvarstatus(var) is not None:
                id_var = int(gvarstatus(var))
                if id_var == chat_id:
                    # إذا كانت القيمة None، نقوم بإضافة القيمة الجديدة
                    delgvar(var)
                    #print(f"تم إضافة القيمة '{new_value}' إلى المتغير '{var}'.")
                    if BOTLOG:
                        await event.client.send_message(BOTLOG_CHATID, f"**• تم حذف المجموعـة.. بنجـاح ☑️**\n**• من قائمـة ڪـروبـات النشـر 🎡**")
                        await event.delete()
                    else:
                        await edit_or_reply(event, f"**• تم حذف المجموعـة.. بنجـاح ☑️**\n**• من قائمـة ڪـروبـات النشـر 🎡**")
                    break
            else:
                #print(f"المتغير '{var}' لديه قيمة: {gvarstatus(var)}.")
                result += 1
    except Exception as e:
        print(e)
    if result == 20 or result == 21:
        return 


# Copyright (C) 2022 t.me/Repthon . All Rights Reserved
@zq_lo.rep_cmd(pattern="السوبرات$")
async def superlist_chat(event):
    # قائمة لتخزين حالة المتغيرات
    var_status = []
    # تحقق من حالة كل متغير
    for var in su_variables:
        status = gvarstatus(var)
        if status is not None:
            var_status.append(status)

    if len(var_status) == 0:
        return await edit_delete(
            event, "**- لا يوجـد كروبـات بعـد فـي قائمـة السوبـرات ؟؟**"
        )
    result = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 **ڪـࢪوبـات السوبـࢪ**\n**⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆**\n"
    for chaat in var_status:
        chaat = int(chaat)
        chat = await get_chatinfo(chaat)
        chat_obj_info = await event.client.get_entity(chat.full_chat.id)
        chat_title = chat_obj_info.title
        result += f"• {chat_title}\n"
    await edit_or_reply(event, result)


async def rrr_all_nasher(zq_lo, sleeptimet, message):
    global r_super
    r_super = True
    #rrr_chats = await zq_lo.get_dialogs()
    # Shuffle the chats to randomize the sending order
    # • ترتيب الإرسال العشوائي
    # يقوم بخلط قائمة الدردشات قبل معالجتها، مما يتوه كاشف السبام الالي لشركة تيليجرام
    #random.shuffle(rrr_chats)
    rrr_chats = []
    async for dialog in zq_lo.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.broadcast:
            continue
        elif (
            isinstance(entity, Channel)
            and entity.megagroup
            or not isinstance(entity, Channel)
            and not isinstance(entity, User)
            and isinstance(entity, Chat)
        ):
            rrr_chats.append(entity.id)
            #if entity.title not in SP_BLACKLIST:
                #rrr_chats.append([entity.title, entity.id])
    
    while r_super:
        for chat in rrr_chats:
            chat_id = int(chat)
            #if chat.is_group and chat.title not in SP_BLACKLIST:
            try:
                # Introduce random delays between 1 and sleeptimet seconds.
                # • التأخيرات العشوائية:
                # تقدم تأخيرات عشوائية بين إرسال الرسائل إلى مجموعات مختلفة.
                # وهذا يجعل نمط الإرسال أقل تجانسًا.
                await asyncio.sleep(random.uniform(2, 10))
                #await asyncio.sleep(random.uniform(1, sleeptimet))  # تعني الأعداد الأصغر (أسرع إرسالًا) (ولكن مخاطرة أعلى للحظر)
            
                if gvarstatus("med_allnasher") is not None:
                    REP_IMG = gvarstatus("med_allnasher")
                    REP = [x for x in REP_IMG.split()]
                    PIC = random.choice(REP)
                    msg_allcaption = gvarstatus("msg_allnasher") if gvarstatus("msg_allnasher") else ""
                    await zq_lo.send_file(chat_id, PIC, caption=msg_allcaption)
                else:
                    caption_nasher = gvarstatus("msg_allnasher")
                    await zq_lo.send_message(chat_id, caption_nasher, link_preview=False)
            
                # Add a delay after each successful message send
                # يقوم بتقديم تأخير بعد كل رسالة ناجحة، مما يقلل بشكل أكبر من اندفاع النشاط
                await asyncio.sleep(random.uniform(11, 20)) # اضبط هذا النطاق بناءً على ملاحظاتك.
        
            except Exception as e:
                #print(f"drrr(276): Error in sending message to chat {chat.id}: {e}")
                # Consider adding more sophisticated error handling, like retry mechanisms
                #await asyncio.sleep(random.uniform(30, 60)) #Longer delay for errors
                #await asyncio.sleep(random.uniform(5, 10)) #Longer delay for errors
                pass
            #else:
                #continue
        
        # Wait for the specified sleeptimet before starting the next round
        await asyncio.sleep(sleeptimet)  # ثواني التأخير بعد كل دورة


async def rr_all_nasher():
    sleeptimet = int(gvarstatus("sec_allnasher"))
    message = gvarstatus("msg_allnasher")
    await rrr_all_nasher(zq_lo, sleeptimet, message)


# ينشر لجميع المجموعات
@zq_lo.rep_cmd(pattern="(نشر_كروبات|نشر_عام)")
async def _(event): # .نشر_كروبات + عدد الثواني بالرد ع الرسالة
    if gvarstatus("status_nasher") or gvarstatus("status_allnasher") or gvarstatus("status_nsuper") or gvarstatus("status_spnasher"):
        return await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية نشر سابقـه مفعله**\n**✧ ارسـل** ( `.ايقاف النشر` ) ** لـ إيقافها اولاً**")
    if not event.reply_to_msg_id:
        await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ ارسـل الامـر بالـرد ع الرسالة المراد نشرها**")
        return
    await event.delete()
    seconds = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    try:
        sleeptimet = int(seconds[0])
        addgvar("sec_allnasher", sleeptimet)
    except Exception:
        return await edit_or_reply(
            event, "**- امـر خاطـىء .. ارسـل ( .النشر ) لـ تصفح اوامـر النشـر التلقائي**"
        )
    #rrr = await edit_or_reply(event, "**✧ جـاري بـدء النشـر في المجموعـات ...الرجـاء الانتظـار**")
    if not os.path.isdir(Config.TEMP_DIR):
        os.makedirs(Config.TEMP_DIR)
    message =  await event.get_reply_message()
    if message.media:
        start = datetime.now()
        downloaded_file_name = await event.client.download_media(
            message, Config.TEMP_DIR
        )
        r_caption = message.text if message.text else None
        delgvar("msg_allnasher")
        if r_caption:
            addgvar("msg_allnasher", r_caption)
        vinfo = None
        if downloaded_file_name.endswith((".webp")):
            resize_image(downloaded_file_name)
        try:
            start = datetime.now()
            vinfo = uploader.upload_file(downloaded_file_name)
        except Exception as exc:
            await event.client.send_message(BOTLOG_CHATID, "**✧ خطا : **" + str(exc))
            os.remove(downloaded_file_name)
        else:
            end = datetime.now()
            ms_two = (end - start).seconds
            os.remove(downloaded_file_name)
            addgvar("med_allnasher", vinfo)
            REP_IMG = gvarstatus("med_allnasher")
            if REP_IMG:
                REP = [x for x in REP_IMG.split()]
                PIC = random.choice(REP)
                await event.client.send_file(BOTLOG_CHATID, PIC, caption=r_caption)
    elif message.text:
        addgvar("msg_allnasher", message.text)
    else:
        return

    zq_lo = event.client
    global r_super
    r_super = True
    rsr = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
    rsr += f"\n<b>• تمت بـدء النشـر .. بنجـاح ✅ </b>"
    if message.media:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n ميديـا 🏕️"
    else:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n نـص 📝"
    rsr += f"\n<b>• المجموعـات :</b> جميـع مجموعات الحسـاب"
    rsr += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
    rsr += f"\n<b>• بـ تأخيـر</b> {seconds} <b>ثانيـه ⏳</b>"
    rsr += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.النشر</code> )"
    rsr += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف النشر</code> )"
    await event.client.send_message(event.chat_id, rsr, parse_mode="html", link_preview=False)
    addgvar("status_allnasher", True)
    if BOTLOG:
        rss = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
        rss += f"\n<b>• تمت بـدء النشـر .. بنجـاح ✅ </b>"
        if message.text:
            rss += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{message.text}</code>"
        rss += f"\n<b>• المجموعـات :</b> جميـع مجموعات الحسـاب"
        rss += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
        rss += f"\n<b>• المجموعـات الهـدف:</b> جميـع مجموعات الحسـاب التي يشتمل اسمها على كلمة (سوبر/Super)""\n<b>• بـ تأخيـر</b> {seconds} <b>ثانيـه ⏳</b>"
        rss += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.النشر</code> )"
        rss += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف النشر</code> )"
        await event.client.send_message(
            BOTLOG_CHATID,
            rss,
            parse_mode="html",
            link_preview=False,
        )
    await rr_all_nasher()


super_groups = ["super", "سوبر"]
async def rrr_supers(zq_lo, sleeptimet, message):
    global r_super
    r_super = True
    rrr_chats = await zq_lo.get_dialogs()
    while r_super:
        for chat in rrr_chats:
            chat_title_lower = chat.title.lower()
            if chat.is_group and any(keyword in chat_title_lower for keyword in super_groups):
                try:
                    # Introduce random delays between 1 and sleeptimet seconds.
                    # • التأخيرات العشوائية:
                    # تقدم تأخيرات عشوائية بين إرسال الرسائل إلى مجموعات مختلفة.
                    # وهذا يجعل نمط الإرسال أقل تجانسًا.
                    await asyncio.sleep(random.uniform(2, 10))
                    #await asyncio.sleep(random.uniform(1, sleeptimet))  # تعني الأعداد الأصغر (أسرع إرسالًا) (ولكن مخاطرة أعلى للحظر)
                    
                    if gvarstatus("med_nsuper") is not None:
                        REP_IMG = gvarstatus("med_nsuper")
                        REP = [x for x in REP_IMG.split()]
                        PIC = random.choice(REP)
                        msg_sucaption = gvarstatus("msg_nsuper") if gvarstatus("msg_nsuper") else ""
                        await zq_lo.send_file(chat.id, PIC, caption=msg_sucaption)
                    else:
                        caption_nasher = gvarstatus("msg_nsuper")
                        await zq_lo.send_message(chat.id, caption_nasher, link_preview=False)
                    
                    # Add a delay after each successful message send
                    # يقوم بتقديم تأخير بعد كل رسالة ناجحة، مما يقلل بشكل أكبر من اندفاع النشاط
                    await asyncio.sleep(random.uniform(11, 20)) # اضبط هذا النطاق بناءً على ملاحظاتك.
                 
                except Exception as e:
                    #print(f"drrr(403): Error in sending message to chat {chat.id}: {e}")
                    # Consider adding more sophisticated error handling, like retry mechanisms
                    #await asyncio.sleep(random.uniform(30, 60)) #Longer delay for errors
                    await asyncio.sleep(random.uniform(5, 10)) #Longer delay for errors
                    pass
        
        # Wait for the specified sleeptimet before starting the next round
        await asyncio.sleep(sleeptimet)


async def rr_supers():
    sleeptimet = int(gvarstatus("sec_nsuper"))
    message = gvarstatus("msg_nsuper")
    await rrr_supers(zq_lo, sleeptimet, message)


# ينشر لمجموعات يوجد ع اسمها كلمة سوبر او super
@zq_lo.rep_cmd(pattern="سوبر")
async def _(event):
    if gvarstatus("status_nasher") or gvarstatus("status_allnasher") or gvarstatus("status_nsuper") or gvarstatus("status_spnasher"):
        return await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ هناك عملية نشر سابقـه مفعله**\n**✧ ارسـل** ( `.ايقاف النشر` ) ** لـ إيقافها اولاً**")
    if not event.reply_to_msg_id:
        await edit_or_reply(event, "**✧ عـذراً .. عـزيـزي ✖️**\n**✧ ارسـل الامـر بالـرد ع الرسالة المراد نشرها**")
        return
    await event.delete()
    await event.delete()
    #rrr = await edit_or_reply(event, "**✧ جـاري بـدء النشـر في المجموعـات ...الرجـاء الانتظـار**")
    seconds = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    #addgvar("sec_nsuper", seconds)
    try:
        sleeptimet = int(seconds[0])
        addgvar("sec_nsuper", sleeptimet)
    except Exception:
        return await edit_or_reply(
            event, "**- امـر خاطـىء .. ارسـل ( .النشر ) لـ تصفح اوامـر النشـر التلقائي**"
        )
    if not os.path.isdir(Config.TEMP_DIR):
        os.makedirs(Config.TEMP_DIR)
    message =  await event.get_reply_message()
    if message.media:
        start = datetime.now()
        downloaded_file_name = await event.client.download_media(
            message, Config.TEMP_DIR
        )
        r_caption = message.text if message.text else None
        delgvar("msg_nsuper")
        if r_caption:
            addgvar("msg_nsuper", r_caption)
        vinfo = None
        if downloaded_file_name.endswith((".webp")):
            resize_image(downloaded_file_name)
        try:
            start = datetime.now()
            vinfo = uploader.upload_file(downloaded_file_name)
        except Exception as exc:
            await event.client.send_message(BOTLOG_CHATID, "**✧ خطا : **" + str(exc))
            os.remove(downloaded_file_name)
        else:
            end = datetime.now()
            ms_two = (end - start).seconds
            os.remove(downloaded_file_name)
            addgvar("med_nsuper", vinfo)
            REP_IMG = gvarstatus("med_nsuper")
            if REP_IMG:
                REP = [x for x in REP_IMG.split()]
                PIC = random.choice(REP)
                await event.client.send_file(BOTLOG_CHATID, PIC, caption=r_caption)
    elif message.text:
        addgvar("msg_nsuper", message.text)
    else:
        return

    zq_lo = event.client
    global r_super
    r_super = True
    rsr = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
    rsr += f"\n<b>• تمت بـدء النشـر .. بنجـاح ✅ </b>"
    if message.media:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n ميديـا 🏕️"
    else:
        rsr += f"\n<b>• نـوع الرسـالة :</b>\n نـص 📝"
    rsr += f"\n<b>• المجموعـات :</b> جميـع مجموعات الحسـاب التي يشتمل اسمها على كلمة (سوبر/Super)"
    rsr += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
    rsr += f"\n<b>• بـ تأخيـر</b> {seconds} <b>ثانيـه ⏳</b>"
    rsr += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.النشر</code> )"
    rsr += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف النشر</code> )"
    await event.client.send_message(event.chat_id, rsr, parse_mode="html", link_preview=False)
    addgvar("status_nsuper", True)
    if BOTLOG:
        rss = "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 <b>النشــࢪ التڪـࢪاࢪي</b>\n<b>⋆┄─┄─┄─┄─┄─┄─┄─┄⋆</b>"
        rss += f"\n<b>• تمت بـدء النشـر .. بنجـاح ✅ </b>"
        if message.text:
            rss += f"\n<b>• الرسـالة المنشـورة :</b>\n<code>{message.text}</code>"
        rss += f"\n<b>• المجموعـات :</b> جميـع مجموعات الحسـاب التي يشتمل اسمها على كلمة (سوبر/Super)"
        rss += f"\n<b>• نشـر تلقائـي .. بلا توقف ♾</b>"
        rss += f"\n<b>• بـ تأخيـر</b> {seconds} <b>ثانيـه ⏳</b>"
        rss += f"\n\n<b>• لـ عـرض اوامـر النشـر ارسـل</b> ( <code>.النشر</code> )"
        rss += f"\n<b>• لـ ايقاف النشـر ارسـل</b> ( <code>.ايقاف النشر</code> )"
        await event.client.send_message(
            BOTLOG_CHATID,
            rss,
            parse_mode="html",
            link_preview=False,
        )
    await rrr_supers(zq_lo, sleeptimet, message)


@zq_lo.rep_cmd(pattern="ايقاف (النشر|نشر|السوبر|سوبر)")
async def stop_super(event):
    global r_super, r_spnasher
    r_super = False
    r_spnasher = False
    if gvarstatus("status_spnasher") is not None:
        delgvar("status_spnasher")
        if gvarstatus("chat_spnasher") is not None:
            delgvar("chat_spnasher")
        if gvarstatus("sec_spnasher") is not None:
            delgvar("sec_spnasher")
        if gvarstatus("msg_spnasher") is not None:
            delgvar("msg_spnasher")
        if gvarstatus("med_spnasher") is not None:
            delgvar("med_spnasher")

    if gvarstatus("status_nasher") is not None:
        delgvar("status_nasher")
        if gvarstatus("chat_nasher") is not None:
            delgvar("chat_nasher")
        if gvarstatus("sec_nasher") is not None:
            delgvar("sec_nasher")
        if gvarstatus("msg_nasher") is not None:
            delgvar("msg_nasher")
        if gvarstatus("med_nasher") is not None:
            delgvar("med_nasher")

    if gvarstatus("status_allnasher") is not None:
        delgvar("status_allnasher")
        if gvarstatus("sec_allnasher") is not None:
            delgvar("sec_allnasher")
        if gvarstatus("msg_allnasher") is not None:
            delgvar("msg_allnasher")
        if gvarstatus("med_allnasher") is not None:
            delgvar("med_allnasher")

    if gvarstatus("status_nsuper") is not None:
        delgvar("status_nsuper")
        if gvarstatus("sec_nasher") is not None:
            delgvar("sec_nasher")
        if gvarstatus("msg_nsuper") is not None:
            delgvar("msg_nsuper")
        if gvarstatus("med_nsuper") is not None:
            delgvar("med_nsuper")

    await event.edit("**- تم إيقاف النشر التلقائي .. بنجاح ✅**")


@zq_lo.rep_cmd(pattern="(اوامر السوبرات|اوامر السوبر)")
async def cmd_super(baqir):
    await edit_or_reply(baqir, BaqirSuper_cmd)


@zq_lo.rep_cmd(pattern="(النشر|اوامر النشر)")
async def cmd_nasher(baqir):
    await edit_or_reply(baqir, BaqirNSH_cmd)


@zq_lo.rep_cmd(pattern="(نشر تلقائي|تلقائي)(?: |$)(.*)")
async def _(event):
    if event.is_private:
        return await edit_or_reply(event, "**✧ عـذراً .. النشر التلقائي خـاص بالقنـوات/المجموعات فقـط\n✧ قم باستخـدام الامـر داخـل القنـاة/المجموعة الهـدف**")
    if input_str := event.pattern_match.group(2):
        try:
            rch = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_or_reply(event, "**✧ عـذراً .. معـرف/ايـدي القنـاة غيـر صـالح**\n**✧ الرجـاء التـأكـد مـن المعـرف/الايـدي**")
        try:
            if is_post(rch.id , event.chat_id):
                return await edit_or_reply(event, "**✧ النشـر التلقـائي مفعـل مسبقـاً ✓**")
            if rch.first_name:
                await asyncio.sleep(1.5)
                add_post(rch.id, event.chat_id)
                await edit_or_reply(event, "**✧ تم تفعيـل النشـر التلقـائي من القنـاة .. بنجـاح ✓**")
        except Exception:
            try:
                if is_post(rch.id , event.chat_id):
                    return await edit_or_reply(event, "**✧ النشـر التلقـائي مفعـل مسبقـاً ✓**")
                if rch.title:
                    await asyncio.sleep(1.5)
                    add_post(rch.id, event.chat_id)
                    return await edit_or_reply(event, "**✧ تم تفعيـل النشـر التلقـائي من القنـاة .. بنجـاح ✓**")
            except Exception as e:
                LOGS.info(str(e))
        await edit_or_reply(event, "**✧ عـذراً .. معـرف/ايـدي القنـاة غيـر صـالح**\n**✧ الرجـاء التـأكـد مـن المعـرف/الايـدي**")


@zq_lo.rep_cmd(pattern="(ايقاف تلقائي|ستوب)(?: |$)(.*)")
async def _(event):
    if event.is_private:
        return await edit_or_reply(event, "**✧ عـذراً .. النشر التلقائي خـاص بالقنـوات/المجموعات فقـط\n✧ قم باستخـدام الامـر داخـل القنـاة/المجموعة الهـدف**")
    if input_str := event.pattern_match.group(2):
        try:
            rch = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_or_reply(event, "**✧ عـذراً .. معـرف/ايـدي القنـاة غيـر صـالح**\n**✧ الرجـاء التـأكـد مـن المعـرف/الايـدي**")
        try:
            if not is_post(rch.id, event.chat_id):
                return await edit_or_reply(event, "**✧ عـذراً .. النشـر التلقـائي غير مفعـل اسـاسـاً ؟!**")
            if rch.first_name:
                await asyncio.sleep(1.5)
                remove_post(rch.id, event.chat_id)
                await edit_or_reply(event, "**✧ تم تعطيـل النشر التلقـائي هنـا .. بنجـاح ✓**")
        except Exception:
            try:
                if not is_post(rch.id, event.chat_id):
                    return await edit_or_reply(event, "**✧ عـذراً .. النشـر التلقـائي غير مفعـل اسـاسـاً ؟!**")
                if rch.title:
                    await asyncio.sleep(1.5)
                    remove_post(rch.id, event.chat_id)
                    return await edit_or_reply(event, "**✧ تم تعطيـل النشر التلقـائي هنـا .. بنجـاح ✓**")
            except Exception as e:
                LOGS.info(str(e))
        await edit_or_reply(event, "**✧ عـذراً .. معـرف/ايـدي القنـاة غيـر صـالح**\n**✧ الرجـاء التـأكـد مـن المعـرف/الايـدي**")


blocked_word = ["sex", "سكس", "نيك", "نيج", "كحاب", "سحاق", "porn"]
blocked_channels = ["ZQ_LO"]


@zq_lo.rep_cmd(pattern="تلي (.*)")
async def _(event):
    search = event.pattern_match.group(1)
    if "sex" in search or "porn" in search or "سكس" in search or "نيك" in search or "نيج" in search or "سحاق" in search or "كحاب" in search or "تبياته" in search:
        return await edit_delete(event, "**- البحث عـن قنـوات غيـر اخلاقيـه محظـور 🔞؟!**", 5)
    l = 'qwertyuiopasdfghjklxcvbnmz'
    result = await zq_lo(functions.contacts.SearchRequest(
        q=search,
        limit=20
    ))
    json = result.to_dict()
    i = str(''.join(random.choice(l) for i in range(3))) + '.txt'
    counter = 0
    for item in json['chats']:
        channel_id = item["username"]
        if channel_id not in blocked_channels:
            links = f'https://t.me/{channel_id}'
            counter += 1
            open(i, 'a').write(f"{counter}• {links}\n")
    link = open(i, 'r').read()
    if not link:
        await event.edit("**- لا توجد نتائج في البحث**")
    else:
        await event.edit(f'''
ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗥𝗘𝗣𝗧𝗛𝗢𝗡 - **بـحـث تيليـجـࢪام**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
l {search} l  **🔎 نتائـج البحث عـن -**
l قنوات + مجموعات l **يشمـل -**

{link}
        ''')


@zq_lo.rep_cmd(pattern="كلمه (.*)")
async def _(event):
    search_word = event.pattern_match.group(1)
    chat = await event.get_chat()
    chat_name = chat.title
    l = 'qwertyuiopasdfghjklxcvbnmz'
    messages = await zq_lo.get_messages(chat, filter=InputMessagesFilterEmpty(), limit=100)
    i = str(''.join(random.choice(l) for i in range(3))) + '.txt'
    counter = 0
    for message in messages:
        if message.message and search_word in message.message:
            links = f'https://t.me/c/{chat.id}/{message.id}'
            counter += 1
            open(i, 'a').write(f"{counter}• {links}\n")
    link = open(i, 'r').read()
    if not link:
        await event.edit("**- لا توجد نتائج في البحث**")
    else:
        await event.edit(f'''
ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗥𝗘𝗣𝗧𝗛𝗢𝗡 - **بـحـث تيليـجـࢪام**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
l {search_word} l  **نتائـج البحث عـن -**
l {chat_name} l  **فـي المجموعـة -**

{link}
        ''')


r = (
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⣾⣿⠁⢸⣿⣧⠀⣿⣿⠉⠹⣿⣆⠉⠉⠉⠉⣿⣿⠟⠀⠀⠀\n"
    "⣿⣿⠀⠘⠛⠛⠀⣿⣿⠀⠀⣿⣿⠀⠀⠀⣼⣿⡟⠀⠀⠀⠀\n"
    "⣿⣿⠀⠀⠀⠀⠀⣿⣿⣤⣾⡿⠃⠀⠀⣼⣿⡟⠀⠀⠀⠀⠀\n"
    "⣿⣿⠀⠀⠀⠀⠀⣿⣿⢻⣿⣇⠀⠀⠀⣿⣿⠁⠀⠀⠀⠀⠀\n"
    "⣿⣿⠀⢸⣿⣷⠀⣿⣿⠀⣿⣿⡄⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀\n"
    "⢻⣿⣦⣼⣿⠏⠀⣿⣿⠀⢸⣿⣧⠀⢀⣿⣿⠀⠀⠀⠀⠀⠀\n"
    "⠈⠛⠛⠛⠋⠀⠀⠛⠛⠀⠀⠛⠛⠀⠸⠛⠛⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⣴⣿⢿⣷⠒⠲⣾⣾⣿⣿⠀⠀⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⣴⣿⠟⠁⠀⢿⣿⠁⣿⣿⣿⠻⣿⣄⠀⠀⠀⠀⠀\n"
    "⠀⠀⣠⡾⠟⠁⠀⠀⠀⢸⣿⣸⣿⣿⣿⣆⠙⢿⣷⡀⠀⠀⠀\n"
    "⣰⡿⠋⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⠀⠀⠉⠻⣿⡀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣆⠂⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⡿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⠿⠟⠀⠀⠻⣿⣿⡇⠀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⠀⢀⣾⡿⠃⠀⠀⠀⠀⠀⠘⢿⣿⡀⠀⠀⠀⠀\n"
    "⠀⠀⠀⠀⠀⣰⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣷⡀⠀⠀⠀\n"
    "⠀⠀⠀⠀⢠⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣧⠀⠀⠀\n"
    "⠀⠀⠀⢀⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣆⠀⠀\n"
    "⠀⠀⠠⢾⠇⠀⠀⠀⠀  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣷⡤.\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀sɪɪɪɪᴜᴜᴜᴜ⠀⠀ ⠀⠀⠀⠀⠀⠀\n"
)




@zq_lo.rep_cmd(pattern="كريس")
async def cr7(crr):
    await crr.edit(r)
    


@zq_lo.rep_cmd(pattern="ماريو")
async def mario(mario):
    await mario.edit(f'''
➖➖➖🟥🟥🟥🟥🟥🟥
➖➖🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥
➖➖🟫🟫🟫🟨🟨🟨⬛🟨
➖🟫🟨🟫🟨🟨🟨🟨⬛🟨🟨🟨
➖🟫🟨🟫🟫🟨🟨🟨🟨⬛🟨🟨
➖🟫🟫🟨🟨🟨🟨🟨⬛⬛⬛⬛
➖➖➖🟨🟨🟨🟨🟨🟨🟨🟨
➖➖🟥🟥🟦🟥🟥🟥🟥
➖🟥🟥🟥🟦🟥🟥🟦🟥🟥🟥
🟥🟥🟥🟥🟦🟦🟦🟦🟥🟥🟥🟥
🟨🟨🟥🟦🟨🟦🟦🟨🟦🟥🟨🟨
🟨🟨🟨🟦🟦🟦🟦🟦🟦🟨🟨🟨
🟨🟨🟦🟦🟦🟦🟦🟦🟦🟦🟨🟨
➖➖🟦🟦🟦➖➖🟦🟦🟦
➖🟫🟫🟫➖➖➖➖🟫🟫🟫
🟫🟫🟫🟫➖➖➖➖🟫🟫🟫🟫
    ''')



@zq_lo.rep_cmd(pattern="ضفدع")
async def frog(frog):
    await frog.edit(f'''
⬜️⬜️🟩🟩⬜️🟩🟩
⬜️🟩🟩🟩⬜️🟩🟩🟩
🟩🟩🟩🟩🟩🟩🟩🟩🟩
🟩⬜️⬛️⬜️🟩⬜️⬛️⬜️🟩
🟩🟩🟩🟩🟩🟩🟩🟩
🟩🟩🟥🟥🟥🟥🟥🟥🟥
🟩??🟥🟥🟥🟥🟥🟥🟥
🟩🟩🟩🟩🟩🟩🟩🟩
    ''')


@zq_lo.rep_cmd(pattern="اجري$")
async def _(kst):
    chars = (
        "🏃                        🦖",
        "🏃                       🦖",
        "🏃                      🦖",
        "🏃                     🦖",
        "🏃                    🦖",
        "🏃                   🦖",
        "🏃                  🦖",
        "🏃                 🦖",
        "🏃                🦖",
        "🏃               🦖",
        "🏃              🦖",
        "🏃             🦖",
        "🏃            🦖",
        "🏃           🦖",
        "🏃          🦖",
        "🏃           🦖",
        "🏃            🦖",
        "🏃             🦖",
        "🏃              🦖",
        "🏃               🦖",
        "🏃                🦖",
        "🏃                 🦖",
        "🏃                  🦖",
        "🏃                   🦖",
        "🏃                    🦖",
        "🏃                     🦖",
        "🏃                    🦖",
        "🏃                   🦖",
        "🏃                  🦖",
        "🏃                 🦖",
        "🏃                🦖",
        "🏃               🦖",
        "🏃              🦖",
        "🏃             🦖",
        "🏃            🦖",
        "🏃           🦖",
        "🏃          🦖",
        "🏃         🦖",
        "🏃        🦖",
        "🏃       🦖",
        "🏃      🦖",
        "🏃     🦖",
        "🏃    🦖",
        "🏃   🦖",
        "🏃  🦖",
        "🏃 🦖",
        "🧎🦖",
    )
    for char in chars:
        await asyncio.sleep(0.3)
        await edit_or_reply(kst, char)


@zq_lo.rep_cmd(pattern="(كلبي|فكيو|ورده|سوفيت|كلوك|تحبني)$")
async def _(kst):
    cmd = kst.pattern_match.group(1)
    if cmd == "كلبي":
        art = r"""
ㅤ
┈┈┈┈╱▏┈┈┈┈┈╱▔▔▔▔╲┈┈┈┈
┈┈┈┈▏▏┈┈┈┈┈▏╲▕▋▕▋▏┈┈┈
┈┈┈┈╲╲┈┈┈┈┈▏┈▏┈▔▔▔▆┈┈
┈┈┈┈┈╲▔▔▔▔▔╲╱┈╰┳┳┳╯┈┈
┈┈╱╲╱╲▏┈┈┈┈┈┈▕▔╰━╯┈┈┈
┈┈▔╲╲╱╱▔╱▔▔╲╲╲╲┈┈┈┈┈┈
┈┈┈┈╲╱╲╱┈┈┈┈╲╲▂╲▂┈┈┈┈
┈┈┈┈┈┈┈┈┈┈┈┈┈╲╱╲╱┈┈┈┈
ㅤ
"""
    elif cmd == "فكيو":
        art = """
ㅤ
⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⣴⠏⠁⠙ ⡄
⠀⠀⠀⠀⠀⠀⠀⠀   ⡾     ⠀⠀ ⢷
⠀⠀⠀⠀⠀⠀   ⠀⠀⣾  ⠀  ⠀  ⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿  ⠀⠀⠀ ⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿  ⠀⠀ ⠀⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿  ⠀⠀⠀ ⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿      ⠀⠀⣿
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⠀⠀⠀⠀⣿⡇
⠀⠀⠀⠀⠀⠀⠀⣾⠏⣿⠀⠀⠀⠀⣿⣷⣦⣄⡀
⠀⠀⠀⠀⠀⠀⣼⡿⠀⣿⠀⠀⠀⠀⣿⠇⠀⠉⢷⡀
⠀⠀⠀⠀⣠⡾⢿⠇⠀⣿⠀⠀⠀⠀⣿⡇⠀⠀⠸⡷⠤⣄⡀
⠀⠀⢠⡾⠋⣾⠀⠀⠀⣿⠀⠀⠀⠀⣿⡇⠀⠀⠀⣧⠀⠀⠹⡄
⠀⣰⠏⠀⠀⣿⠀⠀⠀⠉⠀⠀⠀⠀⠈⠁⠀⠀⠀⢹⡄⠀⠀⢹⡄
⡾⡏⠀⠀⠀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠇⠀⠀⠀⢻⡄
⡾⣿⡀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣷
⠀⠙⢿⣦⡀⠀⠀⠀⠀⠀⠀  ⠀فكيو⠀⠀⠀⠀           ⠀⢠⣿
⠀⠀⠀⠹⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡟
⠀⠀⠀⠀⠈⠻⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠟
⠀⠀⠀⠀⠀⠀⠈⠻⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⡿⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠏
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡏⠀⠀⠀⠀⠀⠀⠀⠀⢸⡏
ㅤ
"""
    elif cmd == "ورده":
        art = """
ㅤ
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀
⠀⠀⠀⠀⠀⠀⠀⡠⠖⠋⠉⠉⠳⡴⠒⠒⠒⠲⠤⢤⣀
⠀⠀⠀⠀⠀⣠⠊⠀⠀⡴⠚⡩⠟⠓⠒⡖⠲⡄⠀⠀⠈⡆
⠀⠀⠀⢀⡞⠁⢠⠒⠾⢥⣀⣇⣚⣹⡤⡟⠀⡇⢠⠀⢠⠇
⠀⠀⠀⢸⣄⣀⠀⡇⠀⠀⠀⠀⠀⢀⡜⠁⣸⢠⠎⣰⣃
⠀⠀⠸⡍⠀⠉⠉⠛⠦⣄⠀⢀⡴⣫⠴⠋⢹⡏⡼⠁⠈⠙⢦⡀
⠀⠀⣀⡽⣄⠀⠀⠀⠀⠈⠙⠻⣎⡁⠀⠀⣸⡾⠀⠀⠀⠀⣀⡹⠂
⢀⡞⠁⠀⠈⢣⡀⠀⠀⠀⠀⠀⠀⠉⠓⠶⢟⠀⢀⡤⠖⠋⠁
⠀⠉⠙⠒⠦⡀⠙⠦⣀⠀⠀⠀⠀⠀⠀⢀⣴⡷⠋
⠀⠀⠀⠀⠀⠘⢦⣀⠈⠓⣦⣤⣤⣤⢶⡟⠁
⢤⣤⣤⡤⠤⠤⠤⠤⣌⡉⠉⠁⠀⢸⢸⠁⡠⠖⠒⠒⢒⣒⡶⣶⠤
⠉⠲⣍⠓⠦⣄⠀⠀⠙⣆⠀⠀⠀⡞⡼⡼⢀⣠⠴⠊⢉⡤⠚⠁
⠀⠀⠈⠳⣄⠈⠙⢦⡀⢸⡀⠀⢰⢣⡧⠷⣯⣤⠤⠚⠉
⠀⠀⠀⠀⠈⠑⣲⠤⠬⠿⠧⣠⢏⡞
⠀⠀⢀⡴⠚⠉⠉⢉⣳⣄⣠⠏⡞
⣠⣴⣟⣒⣋⣉⣉⡭⠟⢡⠏⡼
⠉⠀⠀⠀⠀⠀⠀⠀⢀⠏⣸⠁
⠀⠀⠀⠀⠀⠀⠀⠀⡞⢠⠇
⠀⠀⠀⠀⠀⠀⠀⠘⠓⠚
ㅤ
"""
    elif cmd == "سوفيت":
        art = """
ㅤ
⠀⠀⠀⠀⠀⠀⢀⣤⣀⣀⣀⠀⠻⣷⣄
⠀⠀⠀⠀⢀⣴⣿⣿⣿⡿⠋⠀⠀⠀⠹⣿⣦⡀
⠀⠀⢀⣴⣿⣿⣿⣿⣏⠀⠀⠀⠀⠀⠀⢹⣿⣧
⠀⠀⠙⢿⣿⡿⠋⠻⣿⣿⣦⡀⠀⠀⠀⢸⣿⣿⡆
⠀⠀⠀⠀⠉⠀⠀⠀⠈⠻⣿⣿⣦⡀⠀⢸⣿⣿⡇
⠀⠀⠀⠀⢀⣀⣄⡀⠀⠀⠈⠻⣿⣿⣶⣿⣿⣿⠁
⠀⠀⠀⣠⣿⣿⢿⣿⣶⣶⣶⣶⣾⣿⣿⣿⣿⡁
⢠⣶⣿⣿⠋⠀⠀⠉⠛⠿⠿⠿⠿⠿⠛⠻⣿⣿⣦⡀
⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⡿
ㅤ
"""
    elif cmd == "كلوك":
        art = """
ㅤ
⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⢀⣀⣀⣀⣀⣀⣤⣤
⠀⢶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠛⠛⠛⠛⠛⠋⠉
⠀⠀⢹⣿⣿⣿⣿⣿⠏    ⣿   ⠀ ⢹⡟
⠀⢠⣿⣿⣿⣿⣿⣿⣦⣀⣀⣙⣂⣠⠼⠃
⠀⣾⣿⣿⣿⣿⣿⠁
⢠⣿⣿⣿⣿⣿⡟
⢸⣿⣿⣿⣿⣿⡅
⠀⠛⠛⠛⠛⠛⠃
ㅤ
"""
    elif cmd == "تحبني":
        art = """
ㅤ
⠀⠀⠀⠀⣠⣶⡾⠏⠉⠙⠳⢦⡀⠀⠀⠀⢠⠞⠉⠙⠲⡀
⠀⠀⠀⣴⠿⠏⠀⠀⠀⠀⠀⠀⢳⡀⠀⡏⠀⠀⠀⠀ ⠀⢷
⠀⠀⢠⣟⣋⡀⢀⣀⣀⡀⠀⣀⡀⣧⠀⢸⠀⠀⠀⠀ ⠀ ⡇
⠀⠀⢸⣯⡭⠁⠸⣛⣟⠆⡴⣻⡲⣿⠀⣸⠀تحبني؟   ⡇
⠀⠀⣟⣿⡭⠀⠀⠀⠀⠀⢱⠀⠀⣿⠀⢹⠀⠀⠀ ⠀⠀ ⡇
⠀⠀⠙⢿⣯⠄⠀⠀⠀⢀⡀⠀⠀⡿⠀⠀⡇⠀⠀⠀⠀⡼
⠀⠀⠀⠀⠹⣶⠆⠀⠀⠀⠀⠀⡴⠃⠀⠀⠘⠤⣄⣠⠞
⠀⠀⠀⠀⠀⢸⣷⡦⢤⡤⢤⣞⣁
⠀⠀⢀⣤⣴⣿⣏⠁⠀⠀⠸⣏⢯⣷⣖⣦⡀
⢀⣾⣽⣿⣿⣿⣿⠛⢲⣶⣾⢉⡷⣿⣿⠵⣿
⣼⣿⠍⠉⣿⡭⠉⠙⢺⣇⣼⡏⠀⠀⠀⣄⢸
⣿⣿⣧⣀⣿.........⣀⣰⣏⣘⣆⣀
ㅤ
"""
    await kst.edit(art, parse_mode=parse_pre)


@zq_lo.rep_cmd(pattern="(شبح|دعبل)$")
async def _(kst):
    cmd = kst.pattern_match.group(1)
    if cmd == "شبح":
        expr = """
┻┳|
┳┻| _
┻┳| •.•)  **lشبحl**
┳┻|⊂ﾉ
┻┳|
"""
    elif cmd == "دعبل":
        expr = """
○
く|)へ
    〉
 ￣￣┗┓             __lدعبل مناl__
 　 　   ┗┓　     ヾ○ｼ
  　　        ┗┓   ヘ/
 　                 ┗┓ノ
　 　 　 　 　   ┗┓
"""
    await kst.edit(expr)


if gvarstatus("status_nasher") and gvarstatus("status_nasher") != "false":

    async def srr_nasher():
        seconds = int(gvarstatus("sec_nasher"))
        message = gvarstatus("msg_nasher")
        await zzz_nasher(zq_lo, seconds, message)  # تمرير قيمة seconds هنا لكل مجموعة

    zq_lo.loop.create_task(srr_nasher())


if gvarstatus("status_allnasher") and gvarstatus("status_allnasher") != "false":

    async def srr_all_nasher():
        sleeptimet = int(gvarstatus("sec_allnasher"))
        message = gvarstatus("msg_allnasher")
        await rrr_all_nasher(zq_lo, sleeptimet, message)

    zq_lo.loop.create_task(srr_all_nasher())


if gvarstatus("status_nsuper") and gvarstatus("status_nsuper") != "false":

    async def srr_supers():
        sleeptimet = int(gvarstatus("sec_nsuper"))
        message = gvarstatus("msg_nsuper")
        await rrr_supers(zq_lo, sleeptimet, message)

    zq_lo.loop.create_task(srr_supers())


### قسم مكرر ###
if gvarstatus("status_spnasher") and gvarstatus("status_spnasher") != "false":

    async def srr_spnasher():
        seconds = int(gvarstatus("sec_spnasher"))
        message = gvarstatus("msg_spnasher")
        await rrr_spnasher(zq_lo, seconds, message)  # تمرير قيمة seconds هنا لكل مجموعة

    zq_lo.loop.create_task(srr_spnasher())


### قسم مكرر2 ###
if gvarstatus("status_sp2nasher") and gvarstatus("status_sp2nasher") != "false":

    async def srr_sp2nasher():
        seconds = int(gvarstatus("sec_sp2nasher"))
        message = gvarstatus("msg_sp2nasher")
        await rrr_sp2nasher(zq_lo, seconds, message)  # تمرير قيمة seconds هنا لكل مجموعة

    zq_lo.loop.create_task(srr_sp2nasher())


### قسم مكرر3 ###
if gvarstatus("status_sp3nasher") and gvarstatus("status_sp3nasher") != "false":

    async def srr_sp3nasher():
        seconds = int(gvarstatus("sec_sp3nasher"))
        message = gvarstatus("msg_sp3nasher")
        await rrr_sp3nasher(zq_lo, seconds, message)  # تمرير قيمة seconds هنا لكل مجموعة

    zq_lo.loop.create_task(srr_sp3nasher())
