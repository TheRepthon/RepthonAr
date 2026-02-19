import sys, asyncio
import repthon
from repthon import BOTLOG_CHATID, HEROKU_APP, PM_LOGGER_GROUP_ID
from telethon import functions
from .Config import Config
from .core.logger import logging
from .core.session import zq_lo
from .utils import mybot, autoname, autovars, saves
from .utils import add_bot_to_logger_group, load_plugins, setup_bot, startupmessage, verifyLoggerGroup

LOGS = logging.getLogger("𝐑𝐞𝐩𝐭𝐡𝐨𝐧")
cmdhr = Config.COMMAND_HAND_LER

if not Config.ALIVE_NAME:
    try:
        LOGS.info("⌭ بـدء إضافة الاسـم التلقـائـي ⌭")
        zq_lo.loop.run_until_complete(autoname())
        LOGS.info("✓ تـم إضافة فار الاسـم .. بـنجـاح ✓")
    except Exception as e:
        LOGS.error(f"- {e}")

try:
    LOGS.info("⌭ جـارِ تحميـل الملحقـات ⌭")
    zq_lo.loop.run_until_complete(autovars())
    LOGS.info("✓ تـم تحميـل الملحقـات .. بنجـاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")

try:
    LOGS.info("⌭ بـدء تنزيـل ريبـــثون ⌭")
    zq_lo.loop.run_until_complete(setup_bot())
    LOGS.info("✓ تـم تنزيـل ريبـــثون .. بـنجـاح ✓")
except Exception as e:
    LOGS.error(f"{str(e)}")
    sys.exit()

class RPCheck:
    def __init__(self):
        self.sucess = True
RPcheck = RPCheck()

try:
    LOGS.info("⌭ بـدء إنشـاء البـوت التلقـائـي ⌭")
    zq_lo.loop.run_until_complete(mybot())
    LOGS.info("✓ تـم إنشـاء البـوت .. بـنجـاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")

try:
    LOGS.info("⌭ جـارِ تفعيـل الاشتـراك ⌭")
    zq_lo.loop.create_task(saves())
    LOGS.info("✓ تـم تفعيـل الاشتـراك .. بنجـاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")


async def startup_process():
    await verifyLoggerGroup()
    await load_plugins("plugins")
    await load_plugins("assistant")
    
    B_BLUE  = "\033[1;34m"
    G_GREEN = "\033[1;32m"
    RESET   = "\033[0m"
    
    C1 = "\033[1;35m"
    C2 = "\033[1;33m"
    C3 = "\033[1;36m"
    C4 = "\033[1;91m"
    C5 = "\033[1;94m"
    C6 = "\033[1;92m"
    C7 = "\033[1;96m"

    logo = rf"""
{B_BLUE}╔───────────────────────────────────────╗
│ {C1}____  {C2}          {C3}_   {C4}_                 {B_BLUE}│
│{C1}|  _ \ {C2}___ _ __ {C3}| |_{C4}| |__   {C5}___  {C6}_ __  {B_BLUE}│
│{C1}| |_) {C2}/ _ \ '_ \{C3}| __|{C4} '_ \ {C5}/ _ \{C6}| '_ \ {B_BLUE}│
│{C1}|  _ <{C2}  __/ |_) {C3}| |_|{C4} | | |{C5} (_) {C6}| | | |{B_BLUE}│
│{C1}|_| \_{C2}\___| .__/ {C3}\__|_{C4}| |_|{C5}\___/{C6}|_| |_|{B_BLUE}│
│{C1}      {C2}    |_|   {C3}    {C4}     {C5}     {C6}     {B_BLUE}│
╚───────────────────────────────────────╝{RESET}"""

    done = f"""
{B_BLUE}╔───────────────────────────────────────╗
│ {G_GREEN}⌔ تـم تنصيـب ريبـــثون . . بنجـاح ✓       {B_BLUE}│
│ {G_GREEN}⌔ لـ إظهـار الاوامـر ارسـل ({cmdhr}الاوامر)         {B_BLUE}│
{B_BLUE}╚───────────────────────────────────────╝{RESET}"""
    
    LOGS.info(logo)
    LOGS.info(done)
    await verifyLoggerGroup()
    await add_bot_to_logger_group(BOTLOG_CHATID)
    if PM_LOGGER_GROUP_ID != -100:
        await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
    await startupmessage()
    RPcheck.sucess = True
    return



zq_lo.loop.run_until_complete(startup_process())

if len(sys.argv) not in (1, 3, 4):
    zq_lo.disconnect()
elif not RPcheck.sucess:
    if HEROKU_APP is not None:
        HEROKU_APP.restart()
else:
    try:
        zq_lo.run_until_disconnected()
    except ConnectionError:
        pass
