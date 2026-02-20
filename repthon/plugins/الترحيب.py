# ported from paperplaneExtended by avinashreddy3108 for media support
from telethon import events
from telethon.utils import get_display_name

from repthon import zq_lo
from ..core.logger import logging

from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.welcome_sql import (
    add_welcome_setting,
    get_current_welcome_settings,
    rm_welcome_setting,
    update_previous_welcome,
)
from . import BOTLOG_CHATID

plugin_category = "الخدمات"
LOGS = logging.getLogger(__name__)


@zq_lo.on(events.ChatAction)
async def _(event):  # sourcery no-metrics
    cws = get_current_welcome_settings(event.chat_id)
    if (
        cws
        and (
            event.user_joined
            or event.user_added
            or getattr(event, "user_approved", False)
        )
        and not (await event.get_user()).bot
    ):
        if gvarstatus("clean_welcome") is None:
            try:
                await event.client.delete_messages(
                    event.chat_id, cws.previous_welcome
                )
            except Exception as e:
                LOGS.warning(str(e))

        a_user = await event.get_user()
        chat = await event.get_chat()
        me = await event.client.get_me()
        title = get_display_name(chat) or "لـ هـذه الدردشـة"
        participants = await event.client.get_participants(chat)
        count = len(participants)

        mention = f"<a href='tg://user?id={a_user.id}'>{a_user.first_name}</a>"
        my_mention = f"<a href='tg://user?id={me.id}'>{me.first_name}</a>"

        first = a_user.first_name
        last = a_user.last_name
        fullname = f"{first} {last}" if last else first
        username = f"@{a_user.username}" if a_user.username else mention
        userid = a_user.id

        my_first = me.first_name
        my_last = me.last_name
        my_fullname = f"{my_first} {my_last}" if my_last else my_first
        my_username = f"@{me.username}" if me.username else my_mention

        file_media = None
        current_saved_welcome_message = None
        link_preview = False

        if cws:
            if cws.f_mesg_id:
                msg_o = await event.client.get_messages(
                    entity=BOTLOG_CHATID, ids=int(cws.f_mesg_id)
                )
                file_media = msg_o.media
                current_saved_welcome_message = msg_o.message
                link_preview = True
            elif cws.reply:
                current_saved_welcome_message = cws.reply

        if not current_saved_welcome_message:
            return

        current_message = await event.reply(
            current_saved_welcome_message.format(
                mention=mention,
                title=title,
                count=count,
                first=first,
                last=last,
                fullname=fullname,
                username=username,
                userid=userid,
                my_first=my_first,
                my_last=my_last,
                my_fullname=my_fullname,
                my_username=my_username,
                my_mention=my_mention,
            ),
            file=file_media,
            parse_mode="html",
            link_preview=link_preview,
        )

        update_previous_welcome(event.chat_id, current_message.id)


@zq_lo.rep_cmd(
    pattern="ترحيب(?:\\s|$)([\\s\\S]*)",
    command=("ترحيب", plugin_category),
    info={
        "header": "To welcome new users in chat.",
        "اضـافات التـرحيب": {
            "{mention}": "اضافه منشن",
            "{title}": "اضافة اسم كروب الترحيب",
            "{count}": "اضافة عدد اعضاء الكروب",
            "{first}": "اضافة الاسم الاول",
            "{last}": "اضافة الاسم الاخر",
            "{fullname}": "اضافة الاسم الكامل",
            "{userid}": "اضافة ايدي الشخص",
            "{username}": "اضافة معرف الشخص",
            "{my_first}": "اضافة اسمك الاول",
            "{my_fullname}": "اضافة اسمك الكامل",
            "{my_last}": "اضافة اسمك الاخر",
            "{my_mention}": "اضافة تاك حسابك",
            "{my_username}": "اضافة معرفك",
        },
        "الاسـتخـدام": [
            "{tr}ترحيب + نص الترحيب",
            "{tr}ترحيب بالـرد ع رسالـه ترحيبيـه   او بالـرد ع ميديـا تحتهـا نـص",
        ],
        "مثـال": "{tr}ترحيب اططلـق دخـول {mention}, نـورت مجمـوعتنـا {title} الـخ",
    },
)
async def save_welcome(event):
    "To set welcome message in chat."
    msg = await event.get_reply_message()
    string = "".join(event.text.split(maxsplit=1)[1:])
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG_CHATID:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**⪼ رسـالة التـرحيب :**\
                \n**⪼ ايـدي الـدردشـة :** {event.chat_id}\
                \n**⪼ يتم حفـظ الرسـالة كـ ملاحظـة ترحيبيـة لـ 🔖 :** {get_display_name(await event.get_chat())}, Don't delete this message !!",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID, messages=msg, from_peer=event.chat_id, silent=True
            )
            msg_id = msg_o.id
        else:
            return await edit_or_reply(
                event,
                "**يتطلب حفظ تـرحيب الميـديـا .. تعيين فـار كـروب السجـل ؟!...**",
            )
    elif event.reply_to_msg_id and not string:
        rep_msg = await event.get_reply_message()
        string = rep_msg.text
    success = "**⪼ {} التـرحيب .. بنجـاح فـي هـذه الدردشـه 𓆰.**"
    if add_welcome_setting(event.chat_id, 0, string, msg_id) is True:
        return await edit_or_reply(event, success.format("تـم حفـظ"))
    rm_welcome_setting(event.chat_id)
    if add_welcome_setting(event.chat_id, 0, string, msg_id) is True:
        return await edit_or_reply(event, success.format("تـم تحـديث"))
    await edit_or_reply("**⪼ هنالك خطأ في وضع الترحيب هنا**")


@zq_lo.rep_cmd(
    pattern="حذف الترحيب$",
    command=("حذف الترحيب", plugin_category),
    info={
        "header": "To turn off welcome message in group.",
        "الاسـتخـدام": "{tr}حذف الترحيب",
    },
)
async def del_welcome(event):
    "To turn off welcome message"
    if rm_welcome_setting(event.chat_id) is True:
        await edit_or_reply(event, "**⪼ تـم حـذف التـرحيب .. بنجـاح فـي هـذه الدردشـه 𓆰.**")
    else:
        await edit_or_reply(event, "**⪼ ليـس لـدي اي ترحيبـات هنـا ؟!.**")


@zq_lo.rep_cmd(
    pattern="الترحيبات$",
    command=("الترحيبات", plugin_category),
    info={
        "header": "To check current welcome message in group.",
        "الاسـتخـدام": "{tr}الترحيبات",
    },
)
async def show_welcome(event):
    "To show current welcome message in group"
    cws = get_current_welcome_settings(event.chat_id)
    if not cws:
        return await edit_or_reply(event, "** ⪼ لاتوجد اي رسـاله ترحيب محفوظـه هنـا ؟!...**")
    if cws.f_mesg_id:
        msg_o = await event.client.get_messages(
            entity=BOTLOG_CHATID, ids=int(cws.f_mesg_id)
        )
        await edit_or_reply(
            event, "** ⪼ أرحب حاليًا بالمستخدمين الجدد بهذه الرساله الترحيبية 𓆰.🜝**"
        )
        await event.reply(msg_o.message, file=msg_o.media)
    elif cws.reply:
        await edit_or_reply(
            event, "** ⪼ أرحب حاليًا بالمستخدمين الجدد بهذه الرساله الترحيبية 𓆰.🜝**"
        )
        await event.reply(cws.reply, link_preview=False)


@zq_lo.rep_cmd(
    pattern="cleanwelcome (on|off)$",
    command=("cleanwelcome", plugin_category),
    info={
        "header": "To turn off or turn on of deleting previous welcome message.",
        "description": "if you want to delete previous welcome message and send new one turn on it by deafult it will be on. Turn it off if you need",
        "الاسـتخـدام": "{tr}cleanwelcome <on/off>",
    },
)
async def del_welcome(event):
    "To turn off or turn on of deleting previous welcome message."
    input_str = event.pattern_match.group(1)
    if input_str == "on":
        if gvarstatus("clean_welcome") is None:
            return await edit_delete(event, "__Already it was turned on.__")
        delgvar("clean_welcome")
        return await edit_delete(
            event,
            "__From now on previous welcome message will be deleted and new welcome message will be sent.__",
        )
    if gvarstatus("clean_welcome") is None:
        addgvar("clean_welcome", "false")
        return await edit_delete(
            event, "__From now on previous welcome message will not be deleted .__"
        )
    await edit_delete(event, "It was turned off already")
