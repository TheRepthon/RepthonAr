import os
import asyncio
import random
import requests
import string
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions
from telethon.utils import get_display_name
from urlextract import URLExtract

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from . import BOTLOG, BOTLOG_CHATID, zq_lo, reply_id

LOGS = logging.getLogger(__name__)

plugin_category = "الخدمات"

extractor = URLExtract()
telegraph = Telegraph()
r = telegraph.create_account(short_name=Config.TELEGRAPH_SHORT_NAME)
auth_url = r["auth_url"]



def upload_catbox(file_path):
    url = "https://catbox.moe/user/api.php"

    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                url,
                files={"fileToUpload": file},
                data={"reqtype": "fileupload"},
                timeout=300
            )

        status = response.status_code
        body = response.text.strip()

        LOGS.info(
            "Catbox Response | HTTP: %s | Body: %r",
            status,
            body[:1000]
        )

        if status != 200:
            raise RuntimeError(
                f"Catbox HTTP {status}: {body[:1000]}"
            )

        if not body:
            raise RuntimeError(
                "Catbox returned an empty response."
            )

        if not body.startswith("https://"):
            raise RuntimeError(
                f"Catbox rejected upload: {body[:1000]}"
            )

        return body

    except requests.exceptions.Timeout:
        raise RuntimeError("Catbox upload timed out.")

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Catbox connection failed: {exc}"
        )

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Catbox request error: {exc}"
        )


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")


# Repthon
@zq_lo.rep_cmd(
    pattern="(ت(ل)?ك(راف)?) ?(m|t|ميديا|نص)(?:\\s|$)([\\s\\الله S]*)",
    command=("تلكراف", plugin_category),
    info={
        "header": "رفع ميديا إلى Catbox أو نص إلى Telegraph",
        "options": {
            "m or ميديا": "لرفع الصور والفيديوهات إلى Catbox.",
            "t or نص": "لرفع النصوص إلى Telegraph.",
        },
    },
)
async def _(event):
    repevent = await edit_or_reply(
        event,
        "** ⪼ جاري المعالجه ༗...**"
    )

    optional_title = event.pattern_match.group(5)

    if not event.reply_to_msg_id:
        return await repevent.edit(
            "**⎉╎يجب الرد على رسالة (نص أو ميديا) أولاً..**"
        )

    start = datetime.now()
    r_message = await event.get_reply_message()
    input_str = (event.pattern_match.group(4)).strip()

    if input_str in ["ميديا", "m"]:

        if not r_message.media:
            return await repevent.edit(
                "**⎉╎عذراً، هذا ليس ملف ميديا..**"
            )

        downloaded_file_name = await event.client.download_media(
            r_message,
            Config.TEMP_DIR
        )

        await repevent.edit(
            "** ⪼ تـم التحميـل بنجـاح .. جـاري الـرفـع**"
        )

        try:
            if downloaded_file_name.endswith((".webp")):
                resize_image(downloaded_file_name)

            # رفع الملف باستخدام catbox-uploader
            cat_url = await asyncio.to_thread(
                upload_catbox,
                downloaded_file_name
            )

            if cat_url:
                end = datetime.now()
                ms = (end - start).seconds

                await repevent.edit(
                    f"**⎉╎تم الرفع بنجاح ✅**\n\n"
                    f"**⎉╎الرابط :** [اضغط هنا]({cat_url})\n"
                    f"**⎉╎الوقت :** `{ms} ثانية`",
                    link_preview=True
                )
            else:
                await repevent.edit(
                    "**- فشل الرفع على Catbox..**"
                )

        except Exception as exc:
            LOGS.exception("Catbox Upload Error")

            await repevent.edit(
                f"**- خطـأ : **\n`{exc}`"
            )

        finally:
            if (
                downloaded_file_name
                and os.path.exists(downloaded_file_name)
            ):
                os.remove(downloaded_file_name)

    elif input_str in ["نص", "t"]:

        user_object = await event.client.get_entity(
            r_message.sender_id
        )

        title_of_page = get_display_name(user_object)

        if optional_title:
            title_of_page = optional_title

        page_content = r_message.message or ""

        if r_message.media:
            downloaded_file_name = await event.client.download_media(
                r_message,
                Config.TEMP_DIR
            )

            try:
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()

                for m in m_list:
                    page_content += m.decode("UTF-8") + "\n"

            except:
                pass

            if os.path.exists(downloaded_file_name):
                os.remove(downloaded_file_name)

        if not page_content.strip():
            return await repevent.edit(
                "**⎉╎لا يوجد نص لرفعه..**"
            )

        page_content = page_content.replace("\n", "<br>")

        try:
            response = telegraph.create_page(
                title_of_page,
                html_content=page_content
            )

            rep_url = f"https://graph.org/{response['path']}"

            end = datetime.now()
            ms = (end - start).seconds

            await repevent.edit(
                f"**⎉╎تم رفع النص إلى Telegraph ✅**\n\n"
                f"**⎉╎الرابط :** [اضغط هنا]({rep_url})\n"
                f"**⎉╎الوقت :** `{ms} ثانية`",
                link_preview=True
            )

        except Exception as e:
            await repevent.edit(
                f"**- خطأ في Telegraph:** `{str(e)}`"
            )
