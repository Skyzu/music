import os
import time
from os import path
import random
import asyncio
import shutil
from pytube import YouTube
from yt_dlp import YoutubeDL
from Music import converter
import yt_dlp
import shutil
import psutil
from typing import Callable
from pyrogram import Client
from pyrogram.types import Message, Voice
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from sys import version as pyver
from Music import (
    dbb,
    app,
    BOT_USERNAME,
    BOT_ID,
    BOT_NAME,
    ASSID,
    ASSNAME,
    ASSUSERNAME,
    ASSMENTION,
)
from Music.MusicUtilities.tgcallsrun import (
    music,
    convert,
    download,
    clear,
    get,
    is_empty,
    put,
    task_done,
    ASS_ACC,
)
from Music.MusicUtilities.database.queue import (
    get_active_chats,
    is_active_chat,
    add_active_chat,
    remove_active_chat,
    music_on,
    is_music_playing,
    music_off,
)
from Music.MusicUtilities.database.onoff import (
    is_on_off,
    add_on,
    add_off,
)
from Music.MusicUtilities.database.chats import (
    get_served_chats,
    is_served_chat,
    add_served_chat,
    get_served_chats,
)
from Music.MusicUtilities.helpers.inline import (
    play_keyboard,
    search_markup,
    play_markup,
    playlist_markup,
    audio_markup,
    play_list_keyboard,
)
from Music.MusicUtilities.database.blacklistchat import (
    blacklisted_chats,
    blacklist_chat,
    whitelist_chat,
)
from Music.MusicUtilities.database.gbanned import (
    get_gbans_count,
    is_gbanned_user,
    add_gban_user,
    add_gban_user,
)
from Music.MusicUtilities.database.theme import (
    _get_theme,
    get_theme,
    save_theme,
)
from Music.MusicUtilities.database.assistant import (
    _get_assistant,
    get_assistant,
    save_assistant,
)
from Music.config import DURATION_LIMIT
from Music.MusicUtilities.helpers.decorators import errors
from Music.MusicUtilities.helpers.filters import command
from Music.MusicUtilities.helpers.gets import (
    get_url,
    themes,
    random_assistant,
    ass_det,
)
from Music.MusicUtilities.helpers.logger import LOG_CHAT
from Music.MusicUtilities.helpers.thumbnails import gen_thumb
from Music.MusicUtilities.helpers.chattitle import CHAT_TITLE
from Music.MusicUtilities.helpers.ytdl import ytdl_opts 
from Music.MusicUtilities.helpers.inline import (
    play_keyboard,
    search_markup2,
    search_markup,
)
from pyrogram import filters
from typing import Union
import subprocess
from asyncio import QueueEmpty
import shutil
import os
from youtubesearchpython import VideosSearch
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import Message, Audio, Voice
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

flex = {}
chat_watcher_group = 3


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]))
async def play(_, message: Message):
    chat_id = message.chat.id
    if message.sender_chat:
        return await message.reply_text(
            """
Anda adalah Admin Anonim!
Ubah ke Akun Pengguna Dari Hak Admin.
"""
        )
    user_id = message.from_user.id
    chat_title = message.chat.title
    username = message.from_user.first_name
    checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_on_off(1):
        LOG_ID = "-1001669043727"
        if int(chat_id) != int(LOG_ID):
            return await message.reply_text(
                f"Bot Sedang Dalam Pemeliharaan. Mohon Maaf Untuk Ke Tidak Nyamanannya 🙏.."
            )
        return await message.reply_text(
            f"Bot Sedang Dalam Pemeliharaan. Mohon Maaf Untuk Ke Tidak Nyamanannya 🙏.."
        )
    a = await app.get_chat_member(message.chat.id, BOT_ID)
    if a.status != "administrator":
        await message.reply_text(
            """
**Saya harus menjadi admin dulu dengan beberapa izin? :**

- **dapat mengelola obrolan suara** : `Untuk mengelola obrolan suara`
- **dapat menghapus pesan** : `Untuk menghapus Sampah yang Dicari Musik`
- **dapat mengundang pengguna** : `Untuk mengundang asisten untuk mengobrol`
- **dapat membatasi anggota** : `Untuk Melindungi Musik dari Spam`
"""
        )
        return
    if not a.can_manage_voice_chats:
        await message.reply_text(
            "Saya tidak memiliki izin yang diperlukan untuk melakukan tindakan ini."
            + "\n❌ **MENGELOLA OBROLAN SUARA**"
        )
        return
    if not a.can_delete_messages:
        await message.reply_text(
            "Saya tidak memiliki izin yang diperlukan untuk melakukan tindakan ini."
            + "\n❌ **HAPUS PESAN**"
        )
        return
    if not a.can_invite_users:
        await message.reply_text(
            "I don't have the required permission to perform this action."
            + "\n❌ **UNDANG PENGGUNA MELALUI LINK**"
        )
        return
    if not a.can_restrict_members:
        await message.reply_text(
            "Saya tidak memiliki izin yang diperlukan untuk melakukan tindakan ini."
            + "\n❌ **BAN PENGGUNA**"
        )
        return
    try:
        b = await app.get_chat_member(message.chat.id, ASSID)
        if b.status == "kicked":
            await message.reply_text(
                f"""
{ASSNAME}(@{ASSUSERNAME}) dibanned di obrolan grup anda **{chat_title}**

Unban terlebih dahulu untuk menggunakanya
"""
            )
            return
    except UserNotParticipant:
        if message.chat.username:
            try:
                await ASS_ACC.join_chat(f"{message.chat.username}")
                await message.reply(
                    f"{ASSNAME} Berhasil Bergabung",
                )
                await remove_active_chat(chat_id)
            except Exception as e:
                await message.reply_text(
                    f"""
**Wahk..Asisten Gagal Bergabung Nich**
**Alasan**:{e}
"""
                )
                return
        else:
            try:
                xxy = await app.export_chat_invite_link(message.chat.id)
                yxy = await app.revoke_chat_invite_link(message.chat.id, xxy)
                await ASS_ACC.join_chat(yxy.invite_link)
                await message.reply(
                    f"{ASSNAME} Berhasil Bergabung",
                )
                await remove_active_chat(chat_id)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await message.reply_text(
                    f"""
**Wahk..Asisten Gagal Bergabung Nich**
**Alasan**:{e}
"""
                )
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)
    fucksemx = 0
    if audio:
        fucksemx = 1
        what = "Audio Searched"
        await LOG_CHAT(message, what)
        mystic = await message.reply_text(
            f"**🔄 Sedang Memproses Audio Atas Permintaan Dari {username}**"
        )
        if audio.file_size > 157286400:
            await mystic.edit_text("Ukuran File Audio Harus Kurang dari 150 mb")
            return
        duration = round(audio.duration / 60)
        if duration > DURATION_LIMIT:
            return await mystic.edit_text(
                f"""
**Kesalahan Durasi**

**Durasi yang Diizinkan** : `{DURATION_LIMIT}`
**Durasi yang Diterima** : `{duration}`
"""
            )
        file_name = (
            audio.file_unique_id
            + "."
            + (
                (audio.file_name.split(".")[-1])
                if (not isinstance(audio, Voice))
                else "ogg"
            )
        )
        file_name = path.join(path.realpath("downloads"), file_name)
        file = await convert(
            (await message.reply_to_message.download(file_name))
            if (not path.isfile(file_name))
            else file_name,
        )
        title = "Audio Yang Dipilih Dari Telegram"
        link = "https://t.me/infobotmusik"
        thumb = "cache/Audio.png"
        videoid = "smex1"
    elif url:
        what = "URL Searched"
        await LOG_CHAT(message, what)
        query = message.text.split(None, 1)[1]
        mystic = await message.reply_text("Processing Url")
        ydl_opts = {"format": "bestaudio/best"}
        try:
            results = VideosSearch(query, limit=1)
            for result in results.result()["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"]
                link = result["link"]
                (result["id"])
                videoid = result["id"]
        except Exception as e:
            return await mystic.edit_text(
                f"Lagu Tidak Ditemukan.\n**Kemungkinan Alasan:** {e}"
            )
        smex = int(time_to_seconds(duration))
        if smex > DURATION_LIMIT:
            return await mystic.edit_text(
                f"""
**Wahk..Kesalahan Durasi Nich..**

**Durasi yang Diizinkan** : `{DURATION_LIMIT}`
**Durasi yang Diterima** : `{duration}`
"""
            )
        if duration == "None":
            return await mystic.edit_text("Maaf! Video langsung tidak Didukung")
        if views == "None":
            return await mystic.edit_text("Maaf! Video langsung tidak Didukung")
        semxbabes = f"Downloading {title[:100]}"
        await mystic.edit(semxbabes)
        theme = random.choice(themes)
        ctitle = message.chat.title
        ctitle = await CHAT_TITLE(ctitle)
        userid = message.from_user.id
        thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)

        def my_hook(d):
            if d["status"] == "downloading":
                percentage = d["_percent_str"]
                per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
                per = int(per)
                eta = d["eta"]
                speed = d["_speed_str"]
                size = d["_total_bytes_str"]
                bytesx = d["total_bytes"]
                if str(bytesx) in flex:
                    pass
                else:
                    flex[str(bytesx)] = 1
                if flex[str(bytesx)] == 1:
                    flex[str(bytesx)] += 1
                    try:
                        if eta > 2:
                            mystic.edit(
                                f"Downloading {title[:100]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                    except Exception:
                        pass
                if per > 250:
                    if flex[str(bytesx)] == 2:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            mystic.edit(
                                f"Downloading {title[:100]}..\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 500:
                    if flex[str(bytesx)] == 3:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            mystic.edit(
                                f"Downloading {title[:100]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 800:
                    if flex[str(bytesx)] == 4:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            mystic.edit(
                                f"Downloading {title[:100]}....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
            if d["status"] == "finished":
                try:
                    taken = d["_elapsed_str"]
                except Exception:
                    taken = "00:00"
                size = d["_total_bytes_str"]
                mystic.edit(
                    f"**Downloaded {title[:100]}.....**\n\n**FileSize:** {size}\n**Time Taken:** {taken} sec\n\n**Converting File**[__FFmpeg processing__]"
                )
                print(f"[{videoid}] Downloaded| Elapsed: {taken} seconds")

        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, download, link, my_hook)
        file = await convert(x)
    else:
        if len(message.command) < 2:
            what = "Command"
            await LOG_CHAT(message, what)
            message.from_user.first_name
            hmo = await message.reply_text(
                """
<b>❌ Lagu tidak ditemukan! Coba cari dengan judul lagu yang lebih jelas..

✅ Contoh » `/play desahan manja`
""",
            )
            return
        what = "Query Given"
        await LOG_CHAT(message, what)
        query = message.text.split(None, 1)[1]
        mystic = await message.reply_text("**🔎 Sedang Mencari...**")
        try:
            a = VideosSearch(query, limit=5)
            result = (a.result()).get("result")
            title1 = result[0]["title"]
            duration1 = result[0]["duration"]
            title2 = result[1]["title"]
            duration2 = result[1]["duration"]
            title3 = result[2]["title"]
            duration3 = result[2]["duration"]
            title4 = result[3]["title"]
            duration4 = result[3]["duration"]
            title5 = result[4]["title"]
            duration5 = result[4]["duration"]
            ID1 = result[0]["id"]
            ID2 = result[1]["id"]
            ID3 = result[2]["id"]
            ID4 = result[3]["id"]
            ID5 = result[4]["id"]
        except Exception as e:
            return await mystic.edit_text(
                  """
<b>❌ Lagu tidak ditemukan! Coba cari dengan judul lagu yang lebih jelas..

✅ Contoh » `/play desahan manja`
""",
        )
        thumb = "cache/Results.png"
        await mystic.delete()
        buttons = search_markup(
            ID1,
            ID2,
            ID3,
            ID4,
            ID5,
            duration1,
            duration2,
            duration3,
            duration4,
            duration5,
            user_id,
            query,
        )
        hmo = await message.reply_text(
            f"""
**🎶 Silahkan pilih lagu Mana yang ingin Anda Di Putar..**

1️⃣ <b>{title1[:70]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID3})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :** [Skyzu](https://t.me/skyzusupport)

2️⃣ <b>{title2[:70]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID3})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :** [Skyzu](https://t.me/skyzusupport)

3️⃣ <b>{title3[:70]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID3})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :** [Skyzu](https://t.me/skyzusupport)

4️⃣ <b>{title4[:70]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID4})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :** [Skyzu](https://t.me/skyzusupport)

5️⃣ <b>{title5[:70]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID5})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :** [Skyzu](https://t.me/skyzusupport)
""",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        disable_web_page_preview=True
        return
    if await is_active_chat(chat_id):
        position = await put(chat_id, file=file)
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        cpl = f"downloads/{_chat_}final.png"
        shutil.copyfile(thumb, cpl)
        f20 = open(f"search/{_chat_}title.txt", "w")
        f20.write(f"{title}")
        f20.close()
        f111 = open(f"search/{_chat_}duration.txt", "w")
        f111.write(f"{duration}")
        f111.close()
        f27 = open(f"search/{_chat_}username.txt", "w")
        f27.write(f"{checking}")
        f27.close()
        if fucksemx != 1:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = play_markup(videoid, user_id)
        else:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = audio_markup(videoid, user_id)
        checking = (
            f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        )
        await message.reply_photo(
            photo=thumb,
            caption=f"""
<b>» 𝐌𝐞𝐧𝐚𝐦𝐛𝐚𝐡𝐤𝐚𝐧 𝐝𝐚𝐟𝐭𝐚𝐫 𝐚𝐧𝐭𝐫𝐢𝐚𝐧 𝐥𝐚𝐠𝐮</b>

<b>🏷️ 𝐍𝐚𝐦𝐚 : [{title[:100]}]({link})</b>
<b>⏱️ 𝐃𝐮𝐫𝐚𝐬𝐢 :</b>`{duration}` `Menit`
<b>🎧 𝐀𝐭𝐚𝐬 𝐩𝐞𝐫𝐦𝐢𝐧𝐭𝐚𝐚𝐧 :</b>{checking}

<b>🔢 𝐏𝐨𝐬𝐢𝐬𝐢 𝐚𝐧𝐭𝐫𝐢𝐚𝐧 𝐤𝐞 »</b>{position}
""",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return await mystic.delete()
    else:
        await music_on(chat_id)
        await add_active_chat(chat_id)
        await music.pytgcalls.join_group_call(
            chat_id,
            InputStream(
                InputAudioStream(
                    file,
                ),
            ),
            stream_type=StreamType().local_stream,
        )
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        checking = (
            f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        )
        if fucksemx != 1:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = play_markup(videoid, user_id)
        else:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = audio_markup(videoid, user_id)
        await message.reply_photo(
            photo=thumb,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=f"""
<b>🏷 Nama :</b> [{title[:100]}]({link})
<b>⏱️ Durasi :</b> {duration}
<b>🎧 Atas permintaan :</b> {checking}
<b>⚡ Powered by : [𝐒𝐭𝐞𝐫𝐞𝐨 𝐏𝐫𝐨𝐣𝐞𝐜𝐭](https://t.me/infobotmusik)
""",
        )
        return await mystic.delete()


@Client.on_callback_query(filters.regex(pattern=r"Music"))
async def startyuplay(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    CallbackQuery.message.chat.title
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    try:
        id, duration, user_id = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(
            f"Terjadi Kesalahan!!\n**Mungkin Bisa Karena Alasan**:{e}"
        )
    if duration == "None":
        return await CallbackQuery.message.reply_text(
            f"Sorry!, Live Video Tidak Mendukung"
        )
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Sorry!, Anda Bukan Yang Meminta Lagu Ini", show_alert=True
        )
    await CallbackQuery.message.delete()
    checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
    url = f"https://www.youtube.com/watch?v={id}"
    videoid = id
    smex = int(time_to_seconds(duration))
    if smex > DURATION_LIMIT:
        await CallbackQuery.message.reply_text(
            f"""
**Wahk..Kesalahan Durasi nich..**

**Durasi yang Diizinkan** : `{DURATION_LIMIT}`
**Durasi yang Diterima** : `{duration}`
"""
        )
        return
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            x = ytdl.extract_info(url, download=False)
    except Exception as e:
        return await CallbackQuery.message.reply_text(
            f"Gagal mengunduh video ini..\n\n**Alasan**: {e}"
        )
    title = x["title"]
    mystic = await CallbackQuery.message.reply_text(f"Downloading {title[:50]}")
    thumbnail = x["thumbnail"]
    (x["id"])
    videoid = x["id"]

    def my_hook(d):
        if d["status"] == "downloading":
            percentage = d["_percent_str"]
            per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
            per = int(per)
            eta = d["eta"]
            speed = d["_speed_str"]
            size = d["_total_bytes_str"]
            bytesx = d["total_bytes"]
            if str(bytesx) in flex:
                pass
            else:
                flex[str(bytesx)] = 1
            if flex[str(bytesx)] == 1:
                flex[str(bytesx)] += 1
                try:
                    if eta > 2:
                        mystic.edit(
                            f"Downloading {title[:100]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                except Exception:
                    pass
            if per > 250:
                if flex[str(bytesx)] == 2:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"Downloading {title[:100]}..\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
            if per > 500:
                if flex[str(bytesx)] == 3:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"Downloading {title[:100]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
            if per > 800:
                if flex[str(bytesx)] == 4:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"Mendownload {title[:100]}....\n\n**Ukuran file:** {size}\n**Mendownload:** {percentage}\n**Kecepatan:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
        if d["status"] == "finished":
            try:
                taken = d["_elapsed_str"]
            except Exception:
                taken = "00:00"
            size = d["_total_bytes_str"]
            mystic.edit(
                f"**Downloaded {title[:100]}.....**\n\n**FileSize:** {size}\n**Time Taken:** {taken} sec\n\n**Converting File**[__FFmpeg processing__]"
            )
            print(f"[{videoid}] Downloaded| Elapsed: {taken} seconds")

    loop = asyncio.get_event_loop()
    x = await loop.run_in_executor(None, download, url, my_hook)
    file = await convert(x)
    theme = random.choice(themes)
    ctitle = CallbackQuery.message.chat.title
    ctitle = await CHAT_TITLE(ctitle)
    thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
    await mystic.delete()
    if await is_active_chat(chat_id):
        position = await put(chat_id, file=file)
        buttons = play_markup(videoid, user_id)
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        cpl = f"downloads/{_chat_}final.png"
        shutil.copyfile(thumb, cpl)
        f20 = open(f"search/{_chat_}title.txt", "w")
        f20.write(f"{title}")
        f20.close()
        f111 = open(f"search/{_chat_}duration.txt", "w")
        f111.write(f"{duration}")
        f111.close()
        f27 = open(f"search/{_chat_}username.txt", "w")
        f27.write(f"{checking}")
        f27.close()
        f28 = open(f"search/{_chat_}videoid.txt", "w")
        f28.write(f"{videoid}")
        f28.close()
        await mystic.delete()
        m = await CallbackQuery.message.reply_photo(
            photo=thumb,
            caption=f"""
<b>» 𝐌𝐞𝐧𝐚𝐦𝐛𝐚𝐡𝐤𝐚𝐧 𝐤𝐞 𝐝𝐚𝐟𝐭𝐚𝐫 𝐚𝐧𝐭𝐫𝐢𝐚𝐧 𝐥𝐚𝐠𝐮</b>

<b>🏷 Nama :</b>[{title[:100]}]({url})
<b>⏱️ Durasi :</b> `{duration}` `Menit`
<b>💡 Status : `Dalam antrian`
<b>🎧 Atas permintaan :</b> {checking}
<b>🔢 Posisi antrian ke »</b> `{position}`
""",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        os.remove(thumb)
        await CallbackQuery.message.delete()
    else:
        await music_on(chat_id)
        await add_active_chat(chat_id)
        await music.pytgcalls.join_group_call(
            chat_id,
            InputStream(
                InputAudioStream(
                    file,
                ),
            ),
            stream_type=StreamType().local_stream,
        )
        buttons = play_markup(videoid, user_id)
        await mystic.delete()
        m = await CallbackQuery.message.reply_photo(
            photo=thumb,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=f"""
<b>🏷 Nama :</b> [{title[:100]}]({url})
<b>⏱️ Durasi :</b> `{duration}` `Menit`
<b>💡 Status : `Sedang memutar`
<b>🎧 Atas permintaan :</b> {checking}
<b>⚡ Powered by :</b> [𝐒𝐭𝐞𝐫𝐞𝐨 𝐏𝐫𝐨𝐣𝐞𝐜𝐭](https://t.me/infobotmusik)
""",
        )
        os.remove(thumb)
        await CallbackQuery.message.delete()


@Client.on_callback_query(filters.regex(pattern=r"popat"))
async def popat(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    print(callback_request)
    CallbackQuery.from_user.id
    try:
        id, query, user_id = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(
            f"Terjadi Kesalahan\n**Kemungkinan alasannya adalah**: {e}"
        )
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "This is not for you! Search You Own Song", show_alert=True
        )
    i = int(id)
    query = str(query)
    try:
        a = VideosSearch(query, limit=10)
        result = (a.result()).get("result")
        title1 = result[0]["title"]
        duration1 = result[0]["duration"]
        title2 = result[1]["title"]
        duration2 = result[1]["duration"]
        title3 = result[2]["title"]
        duration3 = result[2]["duration"]
        title4 = result[3]["title"]
        duration4 = result[3]["duration"]
        title5 = result[4]["title"]
        duration5 = result[4]["duration"]
        title6 = result[5]["title"]
        duration6 = result[5]["duration"]
        title7 = result[6]["title"]
        duration7 = result[6]["duration"]
        title8 = result[7]["title"]
        duration8 = result[7]["duration"]
        title9 = result[8]["title"]
        duration9 = result[8]["duration"]
        title10 = result[9]["title"]
        duration10 = result[9]["duration"]
        ID1 = result[0]["id"]
        ID2 = result[1]["id"]
        ID3 = result[2]["id"]
        ID4 = result[3]["id"]
        ID5 = result[4]["id"]
        ID6 = result[5]["id"]
        ID7 = result[6]["id"]
        ID8 = result[7]["id"]
        ID9 = result[8]["id"]
        ID10 = result[9]["id"]
    except Exception as e:
        return await mystic.edit_text(
            f"Lagu Tidak Ditemukan.\\in**Kemungkinan Alasan:** {e}"
        )
    if i == 1:
        buttons = search_markup2(
            ID6,
            ID7,
            ID8,
            ID9,
            ID10,
            duration6,
            duration7,
            duration8,
            duration9,
            duration10,
            user_id,
            query,
        )
        await CallbackQuery.edit_message_text(
            f"""
<b>🎶 **Silahkan pilih lagu mana yang ingin anda putar**</b>

6️⃣ <b>{title6[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID6})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :**  [Skyzu](https://t.me/skyzusupport)

7️⃣ <b>{title7[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID7})
├ ⚡ **Manage by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :**  [Skyzu](https://t.me/skyzusupport)

8️⃣ <b>{title8[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID8})
├ ⚡ **Powered by:** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :**  [Skyzu](https://t.me/skyzusupport)

9️⃣ <b>{title9[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID9})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :**  [Skyzu](https://t.me/skyzusupport)

🔟 <b>{title10[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID10})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :**  [Skyzu](https://t.me/skyzusupport)
""",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        disable_web_page_preview=True
        return
    if i == 2:
        buttons = search_markup(
            ID1,
            ID2,
            ID3,
            ID4,
            ID5,
            duration1,
            duration2,
            duration3,
            duration4,
            duration5,
            user_id,
            query,
        )
        await CallbackQuery.edit_message_text(
            f"""
<b>**🎶 Silahkan pilih lagu mana yang ingin anda putar**</b>

1️⃣ <b>{title1[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID1})
├ ⚡ **powered by:** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **manage by :**  [Skyzu](https://t.me/skyzusupport)

2️⃣ <b>{title2[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID2})
├ ⚡ **powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **manage by :**  [Skyzu](https://t.me/skyzusupport)

3️⃣ <b>{title3[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID3})
├ ⚡ **powered by:** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **manage by :**  [Skyzu](https://t.me/skyzusupport)

4️⃣ <b>{title4[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID4})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **manage by :**  [Skyzu](https://t.me/skyzusupport)

5️⃣ <b>{title5[:100]}</b>
├ 💡 [More Information](https://t.me/{BOT_USERNAME}?start=info_{ID5})
├ ⚡ **Powered by :** [{BOT_NAME}](t.me/{BOT_USERNAME})
└ ☕ **Manage by :**  [Skyzu](https://t.me/skyzusupport)
""",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        disable_web_page_preview=True
        return


@app.on_message(filters.command("playplaylist"))
async def play_playlist_cmd(_, message):
    thumb ="etc/Playlist.jpg"
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    buttons = playlist_markup(user_name, user_id)
    await message.reply_photo(
    photo=thumb, 
    caption=("**__Fitur Daftar Music__**\n\nPilih daftar putar yang ingin Anda mainkan.."),    
    reply_markup=InlineKeyboardMarkup(buttons),
    )
    return


app.on_message(filters.command("playlist") & filters.group)
async def playlist(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await m.delete()
            await m.reply(
                f"**🎵 SEKARANG SEDANG MEMUTAR:** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`",
                disable_web_page_preview=True,
            )
        else:
            QUE = f"**🎵 SEKARANG SEDANG MEMUTAR:** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}` \n\n**⏯ DAFTAR ANTRIAN:**"
            l = len(chat_queue)
            for x in range(1, l):
                hmm = chat_queue[x][0]
                hmmm = chat_queue[x][2]
                hmmmm = chat_queue[x][3]
                QUE = QUE + "\n" + f"**#{x}** - [{hmm}]({hmmm}) | `{hmmmm}`\n"
            await m.reply(QUE, disable_web_page_preview=True)
    else:
        await m.reply("**❌ Tidak ada music yang diputar**")
