from asyncio import QueueEmpty
from pyrogram import Client, filters
from pyrogram.types import Message, Audio, Voice
from Music import app
from Music.MusicUtilities.helpers.decorators import errors
from Music.MusicUtilities.helpers.filters import command, other_filters
from Music.MusicUtilities.database.queue import is_active_chat, add_active_chat, remove_active_chat, music_on, is_music_playing, music_off
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)
import os
import yt_dlp
from youtubesearchpython import VideosSearch
from os import path
import random
import asyncio
import shutil
from time import time
import time as sedtime
from Music import app, dbb, ASSNAME, ASSID, ASSUSERNAME, ASSMENTION, BOT_ID, BOT_USERNAME
from Music.MusicUtilities.tgcallsrun import clear, convert, download, clear, get, music, is_empty, task_done, smexy
from Music.MusicUtilities.helpers.gets import get_url, themes, random_assistant
from pyrogram.types import Message
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputStream
from Music.MusicUtilities.helpers.thumbnails import gen_thumb
from Music.MusicUtilities.helpers.chattitle import CHAT_TITLE
from Music.MusicUtilities.helpers.ytdl import ytdl_opts 
from Music.MusicUtilities.helpers.inline import play_markup, audio_markup
from Music.MusicUtilities.tgcallsrun import (convert, download)
from pyrogram import filters
from typing import Union
from youtubesearchpython import VideosSearch
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant

flex = {}

async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = await app.get_chat_member(chat_id, user_id)
    if member.can_manage_voice_chats:
        perms.append("can_manage_voice_chats")
    return perms
from Music.MusicUtilities.helpers.administrator import adminsOnly

@app.on_message(filters.command("cleandb"))
async def stop_cmd(_, message): 
    chat_id = message.chat.id
    try:
        clear(chat_id)
    except QueueEmpty:
        pass                        
    await remove_active_chat(chat_id)
    try:
        await music.pytgcalls.leave_group_call(chat_id)
    except:
        pass   
    await message.reply_text("**Menghapus Database.**\n**Antrian, Log.**\n**File Mentah,Dan Unduhan.**")
    
@app.on_message(filters.command(["pause", f"pause@{BOT_USERNAME}", "ps"]))
async def pause_cmd(_, message): 
    if message.sender_chat:
        return await message.reply_text("Kamu adalah `Admin Anonim!`\nKembalikan ke Akun Pengguna.") 
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    checking = message.from_user.mention
    chat_id = message.chat.id
    if not await is_active_chat(chat_id):
        return await message.reply_text("❎ Tidak ada music yang diputar di obrolan suara atau VCG")
    elif not await is_music_playing(message.chat.id):
        return await message.reply_text("❎ Tidak ada music yang diputar di obrolan suara atau VCG")   
    await music_off(chat_id)
    await music.pytgcalls.pause_stream(chat_id)
    await message.reply_text(f"⏸ Music Dijeda Oleh {checking}")
    
@app.on_message(filters.command(["resume", f"resume@{BOT_USERNAME}", "rs"]))
async def stop_cmd(_, message): 
    if message.sender_chat:
        return await message.reply_text("Kamu adalah `Admin Anonim!`\nKembalikan ke Akun Pengguna.") 
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    checking = message.from_user.mention
    chat_id = message.chat.id
    if not await is_active_chat(chat_id):
        return await message.reply_text("❎ Tidak ada music yang diputar di obrolan suara atau VCG")
    elif await is_music_playing(chat_id):
        return await message.reply_text("❎ Tidak ada music yang diputar di obrolan suara atau VCG") 
    else:
        await music_on(chat_id)
        await music.pytgcalls.resume_stream(chat_id)
        await message.reply_text(f"**▶️ Music Dilanjutkan Lagi Oleh {checking}**")

@app.on_message(filters.command(["end", f"end@{BOT_USERNAME}", "e"]))
async def stop_cmd(_, message): 
    if message.sender_chat:
        return await message.reply_text("Kamu adalah `Admin Anonim!`\nKembalikan ke Akun Pengguna.") 
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    checking = message.from_user.mention
    chat_id = message.chat.id
    if await is_active_chat(chat_id):
        try:
            clear(chat_id)
        except QueueEmpty:
            pass                        
        await remove_active_chat(chat_id)
        await music.pytgcalls.leave_group_call(chat_id)
        await message.reply_text(f"**❌ Music Telah Dimatikan Oleh {checking}**") 
    else:
        return await message.reply_text("❎ Tidak ada music yang diputar di obrolan suara atau VCG")
    
@app.on_message(filters.command(["skip", f"skip@{BOT_USERNAME}", "sk"]))
async def stop_cmd(_, message): 
    if message.sender_chat:
        return await message.reply_text("Kamu adalah `Admin Anonim!`\nUbah ke Akun Pengguna.") 
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    checking = message.from_user.mention
    chat_id = message.chat.id
    chat_title = message.chat.title
    if not await is_active_chat(chat_id):
        await message.reply_text("**❎ Tidak ada music yang sedang diputar di obrolan suara atau VCG !**")
    else:
        task_done(chat_id)
        if is_empty(chat_id):
            await remove_active_chat(chat_id)
            await message.reply_text("**Tidak ada lagi music di Daftar antrian**\n\nAssistant Bot Music Telah Meninggalkan Obrolan Suara..")
            await music.pytgcalls.leave_group_call(chat_id)
            return  
        else:
            afk = get(chat_id)['file']
            f1 = (afk[0])
            f2 = (afk[1])
            f3 = (afk[2])
            finxx = (f"{f1}{f2}{f3}")
            if str(finxx) != "raw":   
                mystic = await message.reply_text("Musik sedang diputar, Daftar Putar...\n\nMengunduh Musik Berikutnya Dari Daftar Putar....")
                url = (f"https://www.youtube.com/watch?v={afk}")
                try:
                    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                        x = ytdl.extract_info(url, download=False)
                except Exception as e:
                    return await mystic.edit(f"Gagal mengunduh video ini.\n\n**Alasan**:{e}") 
                title = (x["title"])
                videoid = afk
                def my_hook(d):
                    if d['status'] == 'downloading':
                        percentage = d['_percent_str']
                        per = (str(percentage)).replace(".","", 1).replace("%","", 1)
                        per = int(per)
                        eta = d['eta']
                        speed = d['_speed_str']
                        size = d['_total_bytes_str']
                        bytesx = d['total_bytes']
                        if str(bytesx) in flex:
                            pass
                        else:
                            flex[str(bytesx)] = 1
                        if flex[str(bytesx)] == 1:
                            flex[str(bytesx)] += 1
                            sedtime.sleep(1)
                            mystic.edit(f"Sedang Mendownload {title[:70]}\n\n**Ukuruan File :** {size}\n**Mendownload :** {percentage}\n**Kecepatan :** {speed}\n**ETA:** {eta} detik")
                        if per > 500:    
                            if flex[str(bytesx)] == 2:
                                flex[str(bytesx)] += 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"Sedang Mendownload {title[:70]}...\n\n**Ukuran File :** {size}\n**Mendownload :** {percentage}\n**Kecepatan :** {speed}\n**ETA:** {eta} detik")
                                print(f"[{videoid}] Mendownload {percentage} dengan kecepatan {speed} di {chat_title} | ETA: {eta} detik")
                        if per > 800:    
                            if flex[str(bytesx)] == 3:
                                flex[str(bytesx)] += 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"Sedang Mendownload {title[:70]}....\n\n**Ukuran File :** {size}\n**Mendownload :** {percentage}\n**Kecepatan :** {speed}\n**ETA:** {eta} detik")
                                print(f"[{videoid}] Mendownload {percentage} dengan kecepatan {speed} di {chat_title} | ETA: {eta} detik")
                        if per == 1000:    
                            if flex[str(bytesx)] == 4:
                                flex[str(bytesx)] = 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"Sedang Mendownload {title[:70]}.....\n\n**Ukuran File :** {size}\n**Mendownload :** {percentage}\n**Kecepatan :** {speed}\n**ETA:** {eta} detik") 
                                print(f"[{videoid}] Mendownload {percentage} dengan kecepatan {speed} di {chat_title} | ETA: {eta} detik")
                loop = asyncio.get_event_loop()
                xxx = await loop.run_in_executor(None, download, url, my_hook)
                file = await convert(xxx)
                await music.pytgcalls.change_stream(
                    chat_id, 
                    InputStream(
                        InputAudioStream(
                            file,
                        ),
                    ),
                )
                thumbnail = (x["thumbnail"])
                duration = (x["duration"])
                duration = round(x["duration"] / 60)
                theme = random.choice(themes)
                ctitle = (await app.get_chat(chat_id)).title
                ctitle = await CHAT_TITLE(ctitle)
                f2 = open(f'search/{afk}id.txt', 'r')        
                userid =(f2.read())
                thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
                user_id = userid
                buttons = play_markup(videoid, user_id)
                await mystic.delete()
                semx = await app.get_users(userid)
                await message.reply_photo(
                photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"""
<b>⏭️ Melewati Pemutaran Lagu </b>

<b>🏷️ Nama :</b>{title[:70]}
<b>⏱️ Durasi :</b> `{duration}` `Menit`
<b>🎧 Atas Permintaan :</b> {username}
<b>⚡ powered by :</b>[𝐒𝐭𝐞𝐫𝐞𝐨 𝐏𝐫𝐨𝐣𝐞𝐜𝐭](https://t.me/infobotmusik)
""",
                )
                os.remove(thumb)
            else:      
                await music.pytgcalls.change_stream(
                    chat_id, 
                    InputStream(
                        InputAudioStream(
                            afk,
                        ),
                    ),
                )
                _chat_ = ((str(afk)).replace("_","", 1).replace("/","", 1).replace(".","", 1))
                f2 = open(f'search/{_chat_}title.txt', 'r')        
                title =(f2.read())
                f3 = open(f'search/{_chat_}duration.txt', 'r')        
                duration =(f3.read())
                f4 = open(f'search/{_chat_}username.txt', 'r')        
                username =(f4.read())
                f4 = open(f'search/{_chat_}videoid.txt', 'r')        
                videoid =(f4.read())
                user_id = 1
                videoid = str(videoid)
                if videoid == "smex1":
                    buttons = audio_markup(videoid, user_id)
                else:
                    buttons = play_markup(videoid, user_id)
                await message.reply_photo(
                photo=f"downloads/{_chat_}final.png",
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"""
<b>⏭️ Melewati Pemutaran Lagu </b>

<b>🏷️ Nama :</b>{title[:70]}
<b>⏱️ Durasi :</b> `{duration}` `Menit`
<b>🎧 Atas Permintaan :</b> {username}
<b>⚡ powered by :</b>[𝐒𝐭𝐞𝐫𝐞𝐨 𝐏𝐫𝐨𝐣𝐞𝐜𝐭](https://t.me/infobotmusik)
""",
                )
                return

@app.on_message(filters.command(["reload", f"reload@{BOT_USERNAME}"]))
async def reload(_, message):
    chat_id = message.chat.id
    await _.send_message(
    chat_id,
    "✅ 𝘽𝙤𝙩 𝙢𝙪𝙨𝙞𝙘 𝙗𝙚𝙧𝙝𝙖𝙨𝙞𝙡 𝙙𝙞𝙢𝙪𝙡𝙖𝙞 𝙪𝙡𝙖𝙣𝙜.\n\n✅ 𝘿𝙖𝙛𝙩𝙖𝙧 𝙖𝙙𝙢𝙞𝙣 𝙩𝙚𝙡𝙖𝙝 𝙙𝙞𝙥𝙚𝙧𝙗𝙖𝙧𝙪𝙞."
)

