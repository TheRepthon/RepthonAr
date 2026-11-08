import time
import asyncio
import importlib
import logging
import glob
import os
import sys
import urllib.request
from datetime import timedelta
from pathlib import Path
from random import randint
from datetime import datetime as dt
from pytz import timezone
import requests
import heroku3

from telethon import Button, functions, types, utils
from telethon.tl.functions.channels import JoinChannelRequest, EditAdminRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import ChatAdminRights
from telethon.errors import FloodWaitError, FloodError, BadRequestError

from repthon import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID

from ..Config import Config
from ..core.logger import logging
from ..core.session import zq_lo
from ..core.server import web_server
from aiohttp import web
from ..helpers.utils import install_pip
from ..helpers.utils.utils import runcmd
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup

ENV = bool(os.environ.get("ENV", False))
LOGS = logging.getLogger("𝐑𝐞𝐩𝐭𝐡𝐨𝐧")
cmdhr = Config.COMMAND_HAND_LER
Rep_Vip = (1960777228, )
Rep_Dev = (7984777405, )
rchannel = {"@Repthon", "@Repthonn", "@Repthon_up", "@Repthon_vars", "@Repthon_support", "@Repthon_cklaish", "@ZQ_LO", "@xxfir", "@Repthon_help", "@roger21v", "@Devs_Repthon"}
# rprivatech = {"", "", ""}
heroku_api = "https://api.heroku.com"
if Config.HEROKU_APP_NAME is not None and Config.HEROKU_API_KEY is not None:
    Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
    app = Heroku.app(Config.HEROKU_APP_NAME)
    heroku_var = app.config()
else:
    app = None

if ENV:
    VPS_NOLOAD = ["vps"]
elif os.path.exists("config.py"):
    VPS_NOLOAD = ["heroku"]

bot = zq_lo
DEV = 7984777405

async def autovars(): #Code by T.me/RR0RT
    if "ENV" in heroku_var and "TZ" in heroku_var:
        return
    if "ENV" in heroku_var and "TZ" not in heroku_var:
        LOGS.info("جـارِ اضافـة بقيـة الفـارات .. تلقائيـاً")
        rrcom = "."
        rrrtz = "Asia/Baghdad"
        heroku_var["COMMAND_HAND_LER"] = rrcom
        heroku_var["TZ"] = rrrtz
        LOGS.info("تم اضافـة بقيـة الفـارات .. بنجـاح")
    if "ENV" not in heroku_var and "TZ" not in heroku_var:
        LOGS.info("جـارِ اضافـة بقيـة الفـارات .. تلقائيـاً")
        rrenv = "ANYTHING"
        rrcom = "."
        rrrtz = "Asia/Baghdad"
        heroku_var["ENV"] = rrenv
        heroku_var["COMMAND_HAND_LER"] = rrcom
        heroku_var["TZ"] = rrrtz
        LOGS.info("تم اضافـة بقيـة الفـارات .. بنجـاح")

async def autoname(): #Code by T.me/E_7_V
    if gvarstatus("ALIVE_NAME"):
        return
    await bot.start()
    await asyncio.sleep(15)
    LOGS.info("جـارِ اضافة فـار الاسـم التلقـائـي .. انتظـر قليـلاً")
    baqir = await bot.get_me()
    rrname = f"{baqir.first_name} {baqir.last_name}" if baqir.last_name else f"{baqir.first_name}"
    tz = Config.TZ
    tzDateTime = dt.now(timezone(tz))
    rdate = tzDateTime.strftime('%Y/%m/%d')
    militaryTime = tzDateTime.strftime('%H:%M')
    rtime = dt.strptime(militaryTime, "%H:%M").strftime("%I:%M %p")
    rrd = f"‹ {rdate} ›"
    rrt = f"‹ {rtime} ›"
    if gvarstatus("r_date") is None:
        rd = "r_date"
        rt = "r_time"
        rn = "ALIVE_NAME"
        addgvar(rd, rrd)
        addgvar(rt, rrt)
        addgvar(rn, rrname)
    LOGS.info(f"تم اضافـة اسـم المستخـدم {rrname} .. بنجـاح")


async def setup_bot():
    """
    To set up bot for Repthon
    """
    try:
        await zq_lo.connect()
        config = await zq_lo(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == zq_lo.session.server_address:
                if zq_lo.session.dc_id != option.id:
                    LOGS.warning(
                        f"ايـدي DC ثـابت فـي الجلسـة مـن {zq_lo.session.dc_id}"
                        f" الـى {option.id}"
                    )
                zq_lo.session.set_dc(option.id, option.ip_address, option.port)
                zq_lo.session.save()
                break
        bot_details = await zq_lo.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        # await zq_lo.start(bot_token=Config.TG_BOT_USERNAME)
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        baqirport = Config.PORT
        await web.TCPSite(app, bind_address, baqirport).start()
        zq_lo.me = await zq_lo.get_me()
        zq_lo.uid = zq_lo.tgbot.uid = utils.get_peer_id(zq_lo.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(zq_lo.me)
    except Exception as e:
        if "object has no attribute 'tgbot'" in str(e):
            LOGS.error(f"- تـوكـن البـوت المسـاعـد غيـر صالـح او منتهـي - {str(e)}")
        elif "Cannot cast NoneType to any kind of int" in str(e):
            LOGS.error(f"- كـود تيرمكـس غيـر صالـح او منتهـي - {str(e)}")
        elif "was used under two different IP addresses" in str(e):
            LOGS.error(f"- كـود تيرمكـس غيـر صالـح او منتهـي - {str(e)}")
        else:
            LOGS.error(f"كـود تيرمكس - {str(e)}")
        sys.exit()


async def mybot(): #Code by T.me/RR0RT
    if gvarstatus("r_assistant"):
        print("تم تشغيل البوت المسـاعـد .. بنجــاح ✅")
    else:
        Rname = Config.ALIVE_NAME
        Rid = Config.OWNER_ID
        baq_ir = f"[{Rname}](tg://user?id={Rid})"
        Rbotname = Config.TG_BOT_USERNAME
        botname = Config.TG_BOT_USERNAME
        fullname = f"{bot.me.first_name} {bot.me.last_name}" if bot.me.last_name else bot.me.first_name
        try:
            await bot.send_message("@BotFather", "/setinline")
            await asyncio.sleep(2)
            await bot.send_message("@BotFather", botname)
            await asyncio.sleep(2)
            await bot.send_message("@BotFather", fullname)
            await asyncio.sleep(3)
            await bot.send_message("@BotFather", "/setname")
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", botname)
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", fullname)
            await asyncio.sleep(3)
            await bot.send_message("@BotFather", "/setuserpic")
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", botname)
            await asyncio.sleep(1)
            await bot.send_file("@BotFather", "repthon/baqir/Repthon3.jpg")
            await asyncio.sleep(3)
            await bot.send_message("@BotFather", "/setcommands")
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", botname)
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", "start - start the bot")
            await asyncio.sleep(3)
            await bot.send_message("@BotFather", "/setabouttext")
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", botname)
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", f"• البـوت المساعـد ♥️🦾\n• الخاص بـ  {fullname}\n• بوت خدمي متنـوع 🎁")
            await asyncio.sleep(3)
            await bot.send_message("@BotFather", "/setdescription")
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", botname)
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", f"✧ البــوت الخدمـي المسـاعـد\n✧ الخـاص بـ {fullname}\n✧ أحتـوي على عـدة أقسـام خدميـه 🧸♥️\n 🌐 @Repthon 🌐")
            await asyncio.sleep(2)
            await bot.send_message("@BotFather", f"**• إعـداد البـوت المسـاعـد .. تم بنجـاح ☑️**\n**• جـارِ الان بـدء تنصيب سـورس ريبـــثون  ✈️. . .**\n\n**• ملاحظـه هامـه 🔰**\n- هـذه العمليه تحدث تلقائياً .. عبر جلسة التنصيب\n- لـذلك لا داعـي للقلـق 😇")
            addgvar("r_assistant", True)
        except Exception as e:
            print(e)


async def startupmessage():
    """
    Start up message in telegram logger group
    """
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") != "false":
        delgvar("PMLOG")
    if gvarstatus("GRPLOG") and gvarstatus("GRPLOG") != "false":
        delgvar("GRPLOG")
    try:
        if BOTLOG:
            rrr = bot.me
            Rname = f"{rrr.first_name} {rrr.last_name}" if rrr.last_name else rrr.first_name
            Rid = bot.uid
            baq_ir = f"[{Rname}](tg://user?id={Rid})"
            Config.ZQ_LOBLOGO = await zq_lo.tgbot.send_file(
                BOTLOG_CHATID,
                "https://graph.org/file/e7b3ea8dc56ac781d756c.mp4",
                caption=f"**⌔ مرحبـاً عـزيـزي** {Rname} 🫂\n**⌔ تـم تشغـيل سـورس ريبـــثون 🧸♥️**\n**⌔ التنصيب الخاص بـك .. بنجـاح ✅**\n**⌔ لـ تصفح قائمـة الاوامـر 🕹**\n**⌔ ارسـل الامـر** `{cmdhr}مساعده`",
                buttons=[[Button.url("𝗥𝗲𝗽𝘁𝗵𝗼𝗻 🎡 𝗨𝘀𝗲𝗿𝗯𝗼𝘁", "https://t.me/Repthon")], [Button.url("𝗥𝗲𝗽𝘁𝗵𝗼𝗻 𝗦𝘂𝗽𝗽𝗼𝗿𝘁", "https://t.me/Repthon_support")],[Button.url("تواصـل مطـور السـورس", "https://t.me/RR0RT")]]
            )
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        if msg_details:
            await zq_lo.check_testcases()
            message = await zq_lo.get_messages(msg_details[0], ids=msg_details[1])
            text = message.text + "\n\n**•⎆┊تـم اعـادة تشغيـل السـورس بنجــاح 🧸♥️**"
            await zq_lo.edit_message(msg_details[0], msg_details[1], text)
            if gvarstatus("restartupdate") is not None:
                await zq_lo.send_message(
                    msg_details[0],
                    f"{cmdhr}بنك",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
        return None


async def add_bot_to_logger_group(chat_id):
    """
    To add bot to logger groups
    """
    bot_details = await zq_lo.tgbot.get_me()
    try:
        await zq_lo(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await zq_lo(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))
    if chat_id == BOTLOG_CHATID:
        new_rights = ChatAdminRights(
            add_admins=False,
            invite_users=True,
            change_info=False,
            ban_users=False,
            delete_messages=True,
            pin_messages=True,
        )
        rank = "admin"
        try:
            await zq_lo(EditAdminRequest(chat_id, bot_details.username, new_rights, rank))
        except BadRequestError as e:
            LOGS.error(str(e))
        except Exception as e:
            LOGS.error(str(e))


async def saves():
   for Rcc in rchannel:
        try:
             await zq_lo(JoinChannelRequest(channel=Rcc))
             await asyncio.sleep(9)
        except FloodWaitError as rep:
            wait_time = int(rep.seconds)
            waitime = wait_time + 1
            LOGS.error(f"Getting FloodWaitError ({rep.seconds}) - (ImportChatInviteRequest)")
            await asyncio.sleep(waitime) # Add a buffer
            continue
        except OverflowError:
            LOGS.error("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
            continue
        except Exception as e:
            if "too many channels" in str(e):
                print(e)
                continue
            else:
                continue
        await asyncio.sleep(1)

"""
async def supscrips():
   for Rhash in rrprivatech:
        try:
             await zq_lo(functions.messages.ImportChatInviteRequest(hash=Rhash))
             await asyncio.sleep(9)
        except FloodWaitError as rep:
            wait_time = int(rep.seconds)
            waitime = wait_time + 1
            LOGS.error(f"Getting FloodWaitError ({rep.seconds}) - (ImportChatInviteRequest)")
            await asyncio.sleep(waitime) # Add a buffer
            continue
        except OverflowError:
            LOGS.error("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
            continue
        except Exception as e:
            if "too many channels" in str(e):
                print(e)
                continue
            elif "Sleeping for 4s (0:00:04) on ImportChatInviteRequest flood wait" in str(e):  # Sleeping for 4s (0:00:04) on ImportChatInviteRequest flood wait
                print(e)
                await asyncio.sleep(9) # Add a buffer
                continue
            else:
                print(e)
                continue
        await asyncio.sleep(1)
        """

async def load_plugins(folder, extfolder=None):
    """
    To load plugins from the mentioned folder
    """
    if extfolder:
        path = f"{extfolder}/*.py"
        plugin_path = extfolder
    else:
        path = f"repthon/{folder}/*.py"
        plugin_path = f"repthon/{folder}"
    files = glob.glob(path)
    files.sort()
    success = 0
    failure = []
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            pluginname = shortname.replace(".py", "")
            try:
                if (pluginname not in Config.NO_LOAD) and (
                    pluginname not in VPS_NOLOAD
                ):
                    flag = True
                    check = 0
                    while flag:
                        try:
                            load_module(
                                pluginname,
                                plugin_path=plugin_path,
                            )
                            if shortname in failure:
                                failure.remove(shortname)
                            success += 1
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            check += 1
                            if shortname not in failure:
                                failure.append(shortname)
                            if check > 5:
                                break
                else:
                    os.remove(Path(f"{plugin_path}/{shortname}.py"))
            except Exception as e:
                if shortname not in failure:
                    failure.append(shortname)
                os.remove(Path(f"{plugin_path}/{shortname}.py"))
                LOGS.info(
                    f"لا يمكنني تحميل {shortname} بسبب الخطأ {e}\nمجلد القاعده {plugin_path}"
                )
    if extfolder:
        if not failure:
            failure.append("None")
        await zq_lo.tgbot.send_message(
            BOTLOG_CHATID,
            f'Your external repo plugins have imported \n**No of imported plugins :** `{success}`\n**Failed plugins to import :** `{", ".join(failure)}`',
        )



async def verifyLoggerGroup():
    """
    Will verify the both loggers group
    """
    flag = False
    if BOTLOG:
        try:
            entity = await zq_lo.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "- الصلاحيات غير كافيه لأرسال الرسالئل في مجموعه فار ااـ PRIVATE_GROUP_BOT_API_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "لا تمتلك صلاحيات اضافه اعضاء في مجموعة فار الـ PRIVATE_GROUP_BOT_API_ID."
                    )
        except ValueError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID لم يتم العثور عليه . يجب التاكد من ان الفار صحيح."
            )
        except TypeError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID قيمه هذا الفار غير مدعومه. تأكد من انه صحيح."
            )
        except Exception as e:
            LOGS.error(
                "حدث خطأ عند محاولة التحقق من فار PRIVATE_GROUP_BOT_API_ID.\n"
                + str(e)
            )
    else:
        try:
            descript = "لا تقم بحذف هذه المجموعة أو التغيير إلى مجموعة عامه (وظيفتهـا تخزيـن كـل سجـلات وعمليـات البـوت.)"
            photorep = await zq_lo.upload_file(file="baqir/taiba/Repthon1.jpg")
            _, groupid = await create_supergroup(
                "كـروب السجـل ريبـــثون", zq_lo, Config.TG_BOT_USERNAME, descript, photorep
            )
            addgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
            print(
                "المجموعه الخاصه لفار الـ PRIVATE_GROUP_BOT_API_ID تم حفظه بنجاح و اضافه الفار اليه."
            )
            flag = True
        except Exception as e:
            if "can't create channels or chat" in str(e):
                print("- حسابك محظور من شركة تيليجرام وغير قادر على إنشاء مجموعات السجل والتخزين")
            else:
                print(str(e))

    if PM_LOGGER_GROUP_ID != -100:
        try:
            entity = await zq_lo.get_entity(PM_LOGGER_GROUP_ID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        " الصلاحيات غير كافيه لأرسال الرسالئل في مجموعه فار ااـ PM_LOGGER_GROUP_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "لا تمتلك صلاحيات اضافه اعضاء في مجموعة فار الـ  PM_LOGGER_GROUP_ID."
                    )
        except ValueError:
            LOGS.error("PM_LOGGER_GROUP_ID لم يتم العثور على قيمه هذا الفار . تاكد من أنه صحيح .")
        except TypeError:
            LOGS.error("PM_LOGGER_GROUP_ID قيمه هذا الفار خطا. تاكد من أنه صحيح.")
        except Exception as e:
            LOGS.error("حدث خطأ اثناء التعرف على فار PM_LOGGER_GROUP_ID.\n" + str(e))
    else:
        try:
            descript = "لا تقم بحذف هذه المجموعة أو التغيير إلى مجموعة عامه (وظيفتهـا تخزيـن رسـائل الخـاص.)"
            photorep = await zq_lo.upload_file(file="baqir/taiba/Repthon2.jpg")
            _, groupid = await create_supergroup(
                "مجمـوعـة التخـزين", zq_lo, Config.TG_BOT_USERNAME, descript, photorep
            )
            addgvar("PM_LOGGER_GROUP_ID", groupid)
            print("تم عمل المجموعة التخزين بنجاح واضافة الفارات اليه.")
            flag = True
            if flag:
                executable = sys.executable.replace(" ", "\\ ")
                args = [executable, "-m", "repthon"]
                os.execle(executable, *args, os.environ)
                sys.exit(0)
        except Exception as e:
            if "can't create channels or chat" in str(e):
                print("- حسابك محظور من شركة تيليجرام وغير قادر على إنشاء مجموعات السجل والتخزين")
            else:
                print(str(e))


async def install_externalrepo(repo, branch, cfolder):
    repREPO = repo
    rpath = os.path.join(cfolder, "requirements.txt")
    if repBRANCH := branch:
        repourl = os.path.join(repREPO, f"tree/{repBRANCH}")
        gcmd = f"git clone -b {repBRANCH} {repREPO} {cfolder}"
        errtext = f"There is no branch with name `{repBRANCH}` in your external repo {repREPO}. Recheck branch name and correct it in vars(`EXTERNAL_REPO_BRANCH`)"
    else:
        repourl = repREPO
        gcmd = f"git clone {repREPO} {cfolder}"
        errtext = f"The link({repREPO}) you provided for `EXTERNAL_REPO` in vars is invalid. please recheck that link"
    response = urllib.request.urlopen(repourl)
    if response.code != 200:
        LOGS.error(errtext)
        return await zq_lo.tgbot.send_message(BOTLOG_CHATID, errtext)
    await runcmd(gcmd)
    if not os.path.exists(cfolder):
        LOGS.error("- حدث خطأ اثناء استدعاء رابط الملفات الاضافية .. قم بالتأكد من الرابط اولاً...")
        return await zq_lo.tgbot.send_message(BOTLOG_CHATID, "**- حدث خطأ اثناء استدعاء رابط الملفات الاضافية .. قم بالتأكد من الرابط اولاً...**",)
    if os.path.exists(rpath):
        await runcmd(f"pip3 install --no-cache-dir -r {rpath}")
    await load_plugins(folder="repthon", extfolder=cfolder)
