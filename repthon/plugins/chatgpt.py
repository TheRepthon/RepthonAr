# Repthon - Baqir
# Copyright (C) 2023 RepthonArabic. All Rights Reserved
#
# This file is a part of < https://github.com/RepthonArabic/RepthonAr/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/RepthonArabic/RepthonAr/blob/master/LICENSE/>.


import re
import json
import requests
import asyncio
import os
import sys
import urllib.request
import aiohttp
from datetime import timedelta
from telethon import events
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.tl.functions.messages import ImportChatInviteRequest as Get

from . import zq_lo
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

plugin_category = "البوت"


lastResponse = []

async def process_gpt(question):
    global lastResponse
    url = "https://chat-gpt.hazex.workers.dev/"
    data = {
        "gpt": lastResponse,
        "user": str(question)
    }
    timeout = aiohttp.ClientTimeout(total=60)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json(content_type=None)
                if response.status == 200:
                    answer = result.get("answer")
                    if answer:
                        return answer
                    print(f"[GPT] Missing answer: {result}")
                    return False
                print(
                    f"[GPT] HTTP {response.status}: {result}"
                )
                return False
    except asyncio.TimeoutError:
        print("[GPT] Request timed out")
        return False
    except Exception as e:
        print(f"[GPT] Error: {e}")
        return False

async def gpt3_response(query):
    url = f'https://api-1stclass-hashierholmes.vercel.app/gpt/ada?question={query}'
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data.get('message')
    else:
        return "Error fetching response."

async def process_ai_search(question):
    instruction = """
You are an AI search assistant.
Respond like a confident, efficient search engine.

STRICT RULES:
- Answer the question directly.
- Use Markdown formatting.
- Be concise and informative.
- Do not ask follow-up questions.
- Do not suggest additional help.
- Do not offer summaries or next steps.
- Never mention being an AI.
- If facts are uncertain, say: Information may vary.
- End the response immediately after the answer.
"""

    final_prompt = f"{instruction}\n\nSearch query: {question}"
    url = "https://capilotapi.vercel.app/"
    timeout = aiohttp.ClientTimeout(total=45)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                url,
                params={"q": final_prompt}
            ) as response:
                if response.status != 200:
                    return False
                data = await response.json(content_type=None)
                answer = data.get("response", "")
                if not isinstance(answer, str):
                    return False
                blocked_phrases = [
                    "if you want",
                    "i can also",
                    "let me know if",
                    "would you like me"
                ]
                for phrase in blocked_phrases:
                    answer = re.sub(
                        re.escape(phrase) + r".*$",
                        "",
                        answer,
                        flags=re.IGNORECASE | re.DOTALL
                    ).strip()
                return answer if answer else False
    except Exception as e:
        print(f"[Repthon AI Search Error] {e}")
        return False


@zq_lo.rep_cmd(pattern="(?:ai-search|ais|searchai|ai)(?: |$)(.*)")
async def repthon_ai_search(event):
    question = event.pattern_match.group(1).strip()
    if not question and event.reply_to_msg_id:
        replied = await event.get_reply_message()
        if replied and replied.text:
            question = replied.text.strip()
    if not question:
        return await edit_or_reply(
            event,
            "**⎉╎أرسل سؤالك بعد الأمر أو قم بالرد على رسالة.**\n\n"
            "**⎉╎مثال:**\n"
            "`.ai من هو غول دي روجر؟`"
        )
    rep = await edit_or_reply(
        event,
        "**⎉╎جـارِ الاتصـال بـ الذكـاء الاصطناعي 🤖**\n"
        "**⎉╎الرجـاء الانتظـار .. لحظـات**"
    )
    answer = await process_ai_search(question)
    if not answer:
        return await rep.edit(
            "**⎉╎تعذر الحصول على إجابة من خدمة الذكاء الاصطناعي.**\n"
            "**⎉╎يرجى المحاولة لاحقاً.**"
        )
    await rep.edit(
        f"ᯓ 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 𝗔𝗜 𝗦𝗲𝗮𝗿𝗰𝗵 -💡-\n"
        f"**⋆┄─┄─┄─┄─┄─┄─┄─┄─┄⋆**\n\n"
        f"**• س/ {question}**\n\n"
        f"**• الإجابة:**\n{answer}\n\n"
        f"**⋆┄─┄─┄─┄─┄─┄─┄─┄─┄⋆**\n"
        f"𝗥𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁",
        link_preview=False
    )


@zq_lo.rep_cmd(pattern="ريب(?: |$)(.*)")
async def baqir_gpt(event):
    global lastResponse
    if lastResponse is None:
        lastResponse = []
    question = event.pattern_match.group(1)
    rrr = await event.get_reply_message()
    if not question and not event.reply_to_msg_id:
        return await edit_or_reply(event, "**⎉╎بالـرد ع سـؤال او باضـافة السـؤال للامـر**\n**⎉╎مثـــال :**\n`.ريب من هو مكتشف الجاذبية الارضية`")
    if not question and event.reply_to_msg_id and rrr.text: 
        question = rrr.text
    if not event.reply_to_msg_id: 
        question = event.pattern_match.group(1)
    
    if question in ("مسح", "حذف"):
        lastResponse.clear()
        return await edit_or_reply(
            event,
            "**⎉╎تم حذف سجل الذكاء الاصطناعي .. بنجاح ✅**\n"
            "**⎉╎ارسـل الان (.ريب + سؤالك) لـ البـدء من جديد**"
        )

    rep = await edit_or_reply(event, "**⎉╎جـارِ الاتصـال بـ الذكـاء الاصطناعي**\n**⎉╎الرجـاء الانتظـار .. لحظـات**\n\n**⎉╎ملاحظـه 🏷**\n- هذا النموذج يقوم بحفظ الموضوعات السابقة\n- اذا كان لديك اكثر من سؤال لـ نفس الموضوع\n- وتريد تقديم الاسئله رداً على الاجوبة السابقة\n**- لـ مسح سجل تخزين الموضوعات السابقة**\n**- ارسـل الامـر** ( `.ريب مسح` ) **لـ بدء موضوع جديد**")
    answer = await process_gpt(question)
    if answer:
        await rep.edit(f"ᯓ 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 𝗚𝗽𝘁 -💡- **الذكاء الاصطناعي\n⋆┄─┄─┄─┄─┄─┄─┄─┄─┄⋆**\n**• س/ {question}**\n\n• {answer}", link_preview=False)
        lastResponse.append(str(answer))
        if len(lastResponse) > 8:
            lastResponse.pop(0)


@zq_lo.rep_cmd(pattern="س(?: |$)(.*)")
async def baqir_gpt(event):
    question = event.pattern_match.group(1)
    rrr = await event.get_reply_message()
    if not question and not event.reply_to_msg_id:
        return await edit_or_reply(event, "**⎉╎بالـرد ع سـؤال او باضـافة السـؤال للامـر**\n**⎉╎مثـــال :**\n`.س من هو مكتشف الجاذبية الارضية`")
    if not question and event.reply_to_msg_id and rrr.text: 
        question = rrr.text
    if not event.reply_to_msg_id: 
        question = event.pattern_match.group(1)
    rep = await edit_or_reply(event, "**⎉╎جـارِ الاتصـال بـ الذكـاء الاصطناعي\n⎉╎الرجـاء الانتظـار .. لحظـات**")
    answer = await gpt3_response(question)
    await rep.edit(f"ᯓ 𝗥𝗲𝗽𝘁𝗵𝗼𝗻 𝗖𝗵𝗮𝘁𝗚𝗽𝘁 -💡- **الذكاء الاصطناعي\n⋆┄─┄─┄─┄─┄─┄─┄─┄─┄⋆**\n**• س/ {question}**\n\n• {answer}", link_preview=False)


# code by t.me/E_7_V
@zq_lo.rep_cmd(pattern="ريبثون(?: |$)(.*)")
async def repthon_gpt(event):
    baq = event.pattern_match.group(1)
    rrr = await event.get_reply_message()
    chat = "@GPT4Telegrambot"
    if not baq and not event.reply_to_msg_id:
        return await edit_or_reply(event, "**⎉╎بالـرد ع سـؤال او باضـافة السـؤال للامـر**\n**⎉╎مثـــال :**\n`.ريبثون من هو مكتشف الجاذبية الارضية`")
    if not baq and event.reply_to_msg_id and rrr.text:
        baqir = rrr.text
    if not event.reply_to_msg_id:
        baqir = event.pattern_match.group(1)
    rep = await edit_or_reply(event, "**⎉╎جـارِ الاتصـال بـ الذكـاء الاصطنـاعـي\n⎉╎الرجـاء الانتظـار .. لحظـات**")
    async with borg.conversation(chat) as conv:
        try:
            await conv.send_message(baqir)
            repthon = await conv.get_response()
            malak = repthon.text
            if "another 8 seconds" in repthon.text:
                aa = malak.replace("⏳ Please wait another 8 seconds before sending the next question . . .", "**⎉╎يُرجى الانتظار 8 ثوانٍ ⏳\n⎉╎بين ارسـال كل سـؤال والتـالي**") 
                await event.delete()
                return await borg.send_message(event.chat_id, aa)
            await asyncio.sleep(5)
            repthon = await conv.get_response()
            malak = repthon.text
            if "understanding" in repthon.text:
                aa = malak.replace("⏳ Please wait another 8 seconds before sending the next question . . .", "**- عـذراً .. لم أفهم سؤالك\n- قم بـ إعادة صياغته من فضلك؟!**") 
                await event.delete()
                return await borg.send_message(event.chat_id, aa)
            await rep.delete()
            await borg.send_message(event.chat_id, f"**س/ {baqir}\n\n{malak}**\n\n───────────────────\n𝗥𝗲𝗽𝘁𝗵𝗼𝗻 𝗨**ꜱᴇʀʙᴏᴛ** 𝗧**ᴏᴏʟꜱ**\n\t\t\t\t\t\t\t\t𝐁𝐀𝐐𝐈𝐑 • ᴼᵖᵉⁿᴬᴵ")
        except YouBlockedUserError:
            await zq_lo(unblock("GPT4Telegrambot"))
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(baqir)
            repthon = await conv.get_response()
            malak = repthon.text
            if "another 8 seconds" in repthon.text:
                aa = malak.replace("⏳ Please wait another 8 seconds before sending the next question . . .", "**⎉╎يُرجى الانتظار 8 ثوانٍ ⏳\n⎉╎بين ارسـال كل سـؤال والتـالي**") 
                await event.delete()
                return await borg.send_message(event.chat_id, aa)
            await asyncio.sleep(5)
            repthon = await conv.get_response()
            malak = repthon.text
            if "understanding" in repthon.text:
                aa = malak.replace("I'm sorry, I'm not quite understanding the question. Could you please rephrase it?", "**- عـذراً .. لم أفهم سؤالك\n- قم بـ إعادة صياغته من فضلك؟!**") 
                await event.delete()
                return await borg.send_message(event.chat_id, aa)
            if "Please wait a moment" in repthon.text:
                await asyncio.sleep(5)
                repthon = await conv.get_response()
                malak = repthon.text
            await rep.delete()
            await borg.send_message(event.chat_id, f"**س/ {baqir}\n\n{malak}**\n\n───────────────────\n𝗥𝗲𝗽𝘁𝗵𝗼𝗻 𝗨**ꜱᴇʀʙᴏᴛ** 𝗧**ᴏᴏʟꜱ**\n\t\t\t\t\t\t\t\t𝐁𝐀𝐐𝐈𝐑 • ᴼᵖᵉⁿᴬᴵ")


# تخمــط اهينـــك Fuk-You
