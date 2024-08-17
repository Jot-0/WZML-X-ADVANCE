#!/usr/bin/env python3
from datetime import datetime
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, regex, create
from aiofiles import open as aiopen
from aiofiles.os import remove as aioremove, path as aiopath, mkdir
from langcodes import Language
from os import path as ospath, getcwd
from PIL import Image
from time import time
from functools import partial
from html import escape
from io import BytesIO
from asyncio import sleep
from cryptography.fernet import Fernet
import asyncio
from bot import OWNER_ID, LOGGER, bot, user_data, config_dict, categories_dict, DATABASE_URL, IS_PREMIUM_USER, MAX_SPLIT_SIZE
from bot.helper.telegram_helper.message_utils import sendMessage, sendCustomMsg, editMessage, deleteMessage, sendFile, chat_info, user_info
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.ext_utils.db_handler import DbManger
from bot.helper.ext_utils.bot_utils import getdailytasks, update_user_ldata, get_readable_file_size, sync_to_async, new_thread, is_gdrive_link
from bot.helper.mirror_utils.upload_utils.ddlserver.gofile import Gofile
from bot.helper.themes import BotTheme
from bot.helper.nordbotz_utils.react_nordbotz import send_react

handler_dict = {}
desp_dict = {'rcc': ['RCʟᴏɴᴇ ɪs ᴀ ᴄᴏᴍᴍᴀɴᴅ-ʟɪɴᴇ ᴘʀᴏɢʀᴀᴍ ᴛᴏ sʏɴᴄ ғɪʟᴇs ᴀɴᴅ ᴅɪʀᴇᴄᴛᴏʀɪᴇs ᴛᴏ ᴀɴᴅ ғʀᴏᴍ ᴅɪғғᴇʀᴇɴᴛ ᴄʟᴏᴜᴅ sᴛᴏʀᴀɢᴇ ᴘʀᴏᴠɪᴅᴇʀs ʟɪᴋᴇ GDʀɪᴠᴇ, OɴᴇDʀɪᴠᴇ...', 'Sᴇɴᴅ ʀᴄʟᴏɴᴇ.ᴄᴏɴғ. \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'lprefix': ['Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Pʀᴇғɪx ɪs ᴛʜᴇ Fʀᴏɴᴛ Pᴀʀᴛ ᴀᴛᴛᴀᴄᴛᴇᴅ ᴡɪᴛʜ ᴛʜᴇ Fɪʟᴇɴᴀᴍᴇ ᴏғ ᴛʜᴇ Lᴇᴇᴄʜ Fɪʟᴇs.', 'Sᴇɴᴅ Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Pʀᴇғɪx. Dᴏᴄᴜᴍᴇɴᴛᴀᴛɪᴏɴ Hᴇʀᴇ : <a href="https://t.me/NordBotz/511">Cʟɪᴄᴋ Mᴇ</a>  \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'lsuffix': ['Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Sᴜғғɪx ɪs ᴛʜᴇ Eɴᴅ Pᴀʀᴛ ᴀᴛᴛᴀᴄʜᴇᴅ ᴡɪᴛʜ ᴛʜᴇ Fɪʟᴇɴᴀᴍᴇ ᴏғ ᴛʜᴇ Lᴇᴇᴄʜ Fɪʟᴇs', 'Sᴇɴᴅ Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Sᴜғғɪx. Dᴏᴄᴜᴍᴇɴᴛᴀᴛɪᴏɴ Hᴇʀᴇ : <a href="https://t.me/NordBotz511">Cʟɪᴄᴋ Mᴇ</a> \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'lremname': ['Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Rᴇᴍɴᴀᴍᴇ ɪs ᴄᴏᴍʙɪɴᴀᴛɪᴏɴ ᴏғ Rᴇɢᴇx(s) ᴜsᴇᴅ ғᴏʀ ʀᴇᴍᴏᴠɪɴɢ ᴏʀ ᴍᴀɴɪᴘᴜʟᴀᴛɪɴɢ Fɪʟᴇɴᴀᴍᴇ ᴏғ ᴛʜᴇ Lᴇᴇᴄʜ Fɪʟᴇs', 'Sᴇɴᴅ Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Rᴇᴍɴᴀᴍᴇ. Dᴏᴄᴜᴍᴇɴᴛᴀᴛɪᴏɴ Hᴇʀᴇ : <a href="https://t.me/NordBotz/511">Cʟɪᴄᴋ Mᴇ</a> \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'lcaption': ['Lᴇᴇᴄʜ Cᴀᴘᴛɪᴏɴ ɪs ᴛʜᴇ Cᴜsᴛᴏᴍ Cᴀᴘᴛɪᴏɴ ᴏɴ ᴛʜᴇ Lᴇᴇᴄʜ Fɪʟᴇs Uᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴛʜᴇ ʙᴏᴛ', 'Sᴇɴᴅ Lᴇᴇᴄʜ Cᴀᴘᴛɪᴏɴ. Yᴏᴜ ᴄᴀɴ ᴀᴅᴅ HTML ᴛᴀɢs. Dᴏᴄᴜᴍᴇɴᴛᴀᴛɪᴏɴ Hᴇʀᴇ : <a href="https://t.me/NordBotz/511">Cʟɪᴄᴋ Mᴇ</a> \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'ldump': ['Lᴇᴇᴄʜ Fɪʟᴇs Usᴇʀ Dᴜᴍᴘ ғᴏʀ Pᴇʀsᴏɴᴀʟ Usᴇ ᴀs ᴀ Sᴛᴏʀᴀɢᴇ.', 'Sᴇɴᴅ Lᴇᴇᴄʜ Dᴜᴍᴘ Cʜᴀɴɴᴇʟ ID\n➲ <b>Fᴏʀᴍᴀᴛ:</b> \nᴛɪᴛʟᴇ ᴄʜᴀᴛ_ɪᴅ/@ᴜsᴇʀɴᴀᴍᴇ\nᴛɪᴛʟᴇ𝟸 ᴄʜᴀᴛ_ɪᴅ𝟸/@ᴜsᴇʀɴᴀᴍᴇ𝟸. \n\n<b>Nᴏᴛᴇ:</b>Mᴀᴋᴇ Bᴏᴛ Aᴅᴍɪɴ ɪɴ ᴛʜᴇ Cʜᴀɴɴᴇʟ ᴇʟsᴇ ɪᴛ ᴡɪʟʟ ɴᴏᴛ ᴀᴄᴄᴇᴘᴛ\n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'mprefix': ['Mɪʀʀᴏʀ Fɪʟᴇɴᴀᴍᴇ Pʀᴇғɪx ɪs ᴛʜᴇ Fʀᴏɴᴛ Pᴀʀᴛ ᴀᴛᴛᴀᴄᴛᴇᴅ ᴡɪᴛʜ ᴛʜᴇ Fɪʟᴇɴᴀᴍᴇ ᴏғ ᴛʜᴇ Mɪʀʀᴏʀᴇᴅ/Cʟᴏɴᴇᴅ Fɪʟᴇs.', 'Sᴇɴᴅ Mɪʀʀᴏʀ Fɪʟᴇɴᴀᴍᴇ Pʀᴇғɪx. \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'msuffix': ['Mɪʀʀᴏʀ Fɪʟᴇɴᴀᴍᴇ Sᴜғғɪx ɪs ᴛʜᴇ Eɴᴅ Pᴀʀᴛ ᴀᴛᴛᴀᴄʜᴇᴅ ᴡɪᴛʜ ᴛʜᴇ Fɪʟᴇɴᴀᴍᴇ ᴏғ ᴛʜᴇ Mɪʀʀᴏʀᴇᴅ/Cʟᴏɴᴇᴅ Fɪʟᴇs', 'Sᴇɴᴅ Mɪʀʀᴏʀ Fɪʟᴇɴᴀᴍᴇ Sᴜғғɪx. \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'mremname': ['Mɪʀʀᴏʀ Fɪʟᴇɴᴀᴍᴇ Rᴇᴍɴᴀᴍᴇ ɪs ᴄᴏᴍʙɪɴᴀᴛɪᴏɴ ᴏғ Rᴇɢᴇx(s) ᴜsᴇᴅ ғᴏʀ ʀᴇᴍᴏᴠɪɴɢ ᴏʀ ᴍᴀɴɪᴘᴜʟᴀᴛɪɴɢ Fɪʟᴇɴᴀᴍᴇ ᴏғ ᴛʜᴇ Mɪʀʀᴏʀᴇᴅ/Cʟᴏɴᴇᴅ Fɪʟᴇs', 'Sᴇɴᴅ Mɪʀʀᴏʀ Fɪʟᴇɴᴀᴍᴇ Rᴇᴍɴᴀᴍᴇ. \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'thumb': ['Cᴜsᴛᴏᴍ Tʜᴜᴍʙɴᴀɪʟ ᴛᴏ ᴀᴘᴘᴇᴀʀ ᴏɴ ᴛʜᴇ Lᴇᴇᴄʜᴇᴅ ғɪʟᴇs ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴛʜᴇ ʙᴏᴛ', 'Sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ sᴀᴠᴇ ɪᴛ ᴀs ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ. \n<b>Aʟᴛᴇʀɴᴀᴛɪᴠᴇʟʏ:</b> <ᴄᴏᴅᴇ>/ᴄᴍᴅ [ᴘʜᴏᴛᴏ] -s ᴛʜᴜᴍʙ \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'yt_opt': ['Yᴛ-ᴅʟᴘ Oᴘᴛɪᴏɴs ɪs ᴛʜᴇ Cᴜsᴛᴏᴍ Qᴜᴀʟɪᴛʏ ғᴏʀ ᴛʜᴇ ᴇxᴛʀᴀᴄᴛɪᴏɴ ᴏғ ᴠɪᴅᴇᴏs ғʀᴏᴍ ᴛʜᴇ ʏᴛ-ᴅʟᴘ sᴜᴘᴘᴏʀᴛᴇᴅ sɪᴛᴇs.', 'Sᴇɴᴅ YT-DLP Oᴘᴛɪᴏɴs. Tɪᴍᴇᴏᴜᴛ: 𝟼𝟶 sᴇᴄ\nFᴏʀᴍᴀᴛ: ᴋᴇʏ:ᴠᴀʟᴜᴇ|ᴋᴇʏ:ᴠᴀʟᴜᴇ|ᴋᴇʏ:ᴠᴀʟᴜᴇ.\nExᴀᴍᴘʟᴇ: ғᴏʀᴍᴀᴛ:ʙᴠ*+ᴍᴇʀɢᴇᴀʟʟ[ᴠᴄᴏᴅᴇᴄ=ɴᴏɴᴇ]|ɴᴏᴄʜᴇᴄᴋᴄᴇʀᴛɪғɪᴄᴀᴛᴇ:Tʀᴜᴇ\nCʜᴇᴄᴋ ᴀʟʟ ʏᴛ-ᴅʟᴘ ᴀᴘɪ ᴏᴘᴛɪᴏɴs ғʀᴏᴍ ᴛʜɪs  <a href="https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184">Fɪʟᴇ</a> ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴄʟɪ ᴀʀɢᴜᴍᴇɴᴛs ᴛᴏ ᴀᴘɪ ᴏᴘᴛɪᴏɴs.'],
            'usess': [f'Usᴇʀ Sᴇssɪᴏɴ ɪs Tᴇʟᴇɢʀᴀᴍ Sᴇssɪᴏɴ ᴜsᴇᴅ ᴛᴏ Dᴏᴡɴʟᴏᴀᴅ Pʀɪᴠᴀᴛᴇ Cᴏɴᴛᴇɴᴛs ғʀᴏᴍ Pʀɪᴠᴀᴛᴇ Cʜᴀɴɴᴇʟs ᴡɪᴛʜ ɴᴏ ᴄᴏᴍᴘʀᴏᴍɪsᴇ ɪɴ Pʀɪᴠᴀᴄʏ, Bᴜɪʟᴅ ᴡɪᴛʜ Eɴᴄʀʏᴘᴛɪᴏɴ.\n{"<b>Wᴀʀɴɪɴɢ:</b> Tʜɪs Bᴏᴛ ɪs ɴᴏᴛ sᴇᴄᴜʀᴇᴅ. Wᴇ ʀᴇᴄᴏᴍᴍᴇɴᴅ ᴀsᴋɪɴɢ ᴛʜᴇ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴛᴏ sᴇᴛ ᴛʜᴇ Uᴘsᴛʀᴇᴀᴍ ʀᴇᴘᴏ ᴛᴏ ᴛʜᴇ Oғғɪᴄɪᴀʟ ʀᴇᴘᴏ. Iғ ɪᴛ ɪs ɴᴏᴛ ᴛʜᴇ ᴏғғɪᴄɪᴀʟ ʀᴇᴘᴏ, ᴛʜᴇɴ Nord Botz ɪs ɴᴏᴛ ʀᴇsᴘᴏɴsɪʙʟᴇ ғᴏʀ ᴀɴʏ ɪssᴜᴇs ᴛʜᴀᴛ ᴍᴀʏ ᴏᴄᴄᴜʀ ɪɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ." if config_dict["UPSTREAM_REPO"] != "https://github.com/Jot4349/WZML-X-ADVANCE" else "Bᴏᴛ ɪs Sᴇᴄᴜʀᴇ. Yᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴇ sᴇssɪᴏɴ sᴇᴄᴜʀᴇʟʏ."}', 'Sᴇɴᴅ ʏᴏᴜʀ Sᴇssɪᴏɴ Sᴛʀɪɴɢ.\n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'split_size': ['Lᴇᴇᴄʜ Sᴘʟɪᴛs Sɪᴢᴇ ɪs ᴛʜᴇ sɪᴢᴇ ᴛᴏ sᴘʟɪᴛ ᴛʜᴇ Lᴇᴇᴄʜᴇᴅ Fɪʟᴇ ʙᴇғᴏʀᴇ ᴜᴘʟᴏᴀᴅɪɴɢ', f'Sᴇɴᴅ Lᴇᴇᴄʜ sᴘʟɪᴛ sɪᴢᴇ ɪɴ ᴀɴʏ ᴄᴏᴍғᴏʀᴛᴀʙʟᴇ sɪᴢᴇ, ʟɪᴋᴇ 𝟸Gʙ, 𝟻𝟶𝟶MB ᴏʀ 𝟷.𝟺𝟼ɢB. \n<b>PREMIUM ACTIVE:</b> {IS_PREMIUM_USER}. \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'ddl_servers': ['Dᴅʟ Sᴇʀᴠᴇʀs ᴡʜɪᴄʜ ᴜᴘʟᴏᴀᴅs ʏᴏᴜʀ Fɪʟᴇ ᴛᴏ ᴛʜᴇɪʀ Sᴘᴇᴄɪғɪᴄ Hᴏsᴛɪɴɢ', ''],
            'user_tds': [f'UsᴇʀTD ʜᴇʟᴘs ᴛᴏ Uᴘʟᴏᴀᴅ ғɪʟᴇs ᴠɪᴀ Bᴏᴛ ᴛᴏ ʏᴏᴜʀ Cᴜsᴛᴏᴍ Dʀɪᴠᴇ Dᴇsᴛɪɴᴀᴛɪᴏɴ ᴠɪᴀ Gʟᴏʙᴀʟ SA ᴍᴀɪʟ\n\n➲ <b>SA Mᴀɪʟ :</b> {"Not Specified" if "USER_TD_SA" not in config_dict else config_dict["USER_TD_SA"]}', 'Sᴇɴᴅ Usᴇʀ TD ᴅᴇᴛᴀɪʟs ғᴏʀ Usᴇ ᴡʜɪʟᴇ Mɪʀʀᴏʀ/Cʟᴏɴᴇ\n➲ <b>Fᴏʀᴍᴀᴛ:</b>\nɴᴀᴍᴇ ɪᴅ/ʟɪɴᴋ ɪɴᴅᴇx(ᴏᴘᴛɪᴏɴᴀʟ)\ɴɴᴀᴍᴇ𝟸 ʟɪɴᴋ𝟸/ɪᴅ𝟸 ɪɴᴅᴇx(ᴏᴘᴛɪᴏɴᴀʟ)\n\n<b>NOTE:</b>\n<i>𝟷. Dʀɪᴠᴇ ID ᴍᴜsᴛ ʙᴇ ᴠᴀʟɪᴅ, ᴛʜᴇɴ ᴏɴʟʏ ɪᴛ ᴡɪʟʟ ᴀᴄᴄᴇᴘᴛ\n𝟸. Nᴀᴍᴇs ᴄᴀɴ ʜᴀᴠᴇ sᴘᴀᴄᴇs\n𝟹. Aʟʟ UsᴇʀTDs ᴀʀᴇ ᴜᴘᴅᴀᴛᴇᴅ ᴏɴ ᴇᴠᴇʀʏ ᴄʜᴀɴɢᴇ\n𝟺. Tᴏ ᴅᴇʟᴇᴛᴇ sᴘᴇᴄɪғɪᴄ UsᴇʀTD, ɢɪᴠᴇ Nᴀᴍᴇ(s) sᴇᴘᴀʀᴀᴛᴇᴅ ʙʏ ᴇᴀᴄʜ ʟɪɴᴇ</i>\n\n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ'],
            'gofile': ['Gᴏғɪʟᴇ ɪs ᴀ ғʀᴇᴇ ғɪʟᴇ sʜᴀʀɪɴɢ ᴀɴᴅ sᴛᴏʀᴀɢᴇ ᴘʟᴀᴛғᴏʀᴍ. Yᴏᴜ ᴄᴀɴ sᴛᴏʀᴇ ᴀɴᴅ sʜᴀʀᴇ ʏᴏᴜʀ ᴄᴏɴᴛᴇɴᴛ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ʟɪᴍɪᴛ.', "Sᴇɴᴅ GᴏFɪʟᴇ's API Kᴇʏ. Gᴇᴛ ɪᴛ ᴏɴ ʜᴛᴛᴘs://ɢᴏғɪʟᴇ.ɪᴏ/ᴍʏPʀᴏғɪʟᴇ, Iᴛ ᴡɪʟʟ ɴᴏᴛ ʙᴇ Aᴄᴄᴇᴘᴛᴇᴅ ɪғ ᴛʜᴇ API Kᴇʏ ɪs Iɴᴠᴀʟɪᴅ !!\n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ"],
            'streamtape': ['Sᴛʀᴇᴀᴍᴛᴀᴘᴇ ɪs ғʀᴇᴇ Vɪᴅᴇᴏ Sᴛʀᴇᴀᴍɪɴɢ & sʜᴀʀɪɴɢ Hᴏsᴛᴇʀ', "Sᴇɴᴅ SᴛʀᴇᴀᴍTᴀᴘᴇ's Lᴏɢɪɴ ᴀɴᴅ Kᴇʏ\n<b>Fᴏʀᴍᴀᴛ:</b> <code>ᴜsᴇʀ_ʟᴏɢɪɴ:ᴘᴀss_ᴋᴇʏ</code>\n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ"],
            'lmeta': ['Yᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ ᴛʜᴀᴛ ᴡɪʟʟ ʙᴇ ᴜsᴇᴅ ᴡʜɪʟᴇ ᴇᴅɪᴛɪɴɢ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴏғ ᴛʜᴇ ᴠɪᴅᴇᴏ ғɪʟᴇ', 'Sᴇɴᴅ Mᴇᴛᴀᴅᴀᴛᴀ Tᴇxᴛ Fᴏʀ Lᴇᴇᴄʜɪɴɢ Fɪʟᴇs. \n <b>Wʜᴀᴛ ɪs Mᴇᴛᴀᴅᴀᴛᴀ? 👉 <a href="https://te.legra.ph/What-is-Metadata-07-03">Cʟɪᴄᴋ Hᴇʀᴇ</a></b> \n<b>Tɪᴍᴇᴏᴜᴛ:</b> 𝟼𝟶 sᴇᴄ.'],
            }
fname_dict = {'rcc': 'RCʟᴏɴᴇ',
             'lprefix': 'Pʀᴇғɪx',
             'lsuffix': 'Sᴜғғɪx',
             'lremname': 'Rᴇᴍɴᴀᴍᴇ',
             'lmeta': 'Mᴇᴛᴀᴅᴀᴛᴀ',
             'mprefix': 'Pʀᴇғɪx',
             'msuffix': 'Suffix',
             'mremname': 'Rᴇᴍɴᴀᴍᴇ',
             'ldump': 'Usᴇʀ Dᴜᴍᴘ',
             'lcaption': 'Cᴀᴘᴛɪᴏɴ',
             'thumb': 'Tʜᴜᴍʙɴᴀɪʟ',
             'yt_opt': 'Yᴛ-Dʟᴘ Oᴘᴛɪᴏɴs',
             'usess': 'Usᴇʀ Sᴇssɪᴏɴ',
             'split_size': 'Lᴇᴇᴄʜ Sᴘʟɪᴛs',
             'ddl_servers': 'DDL Sᴇʀᴠᴇʀs',
             'user_tds': 'Usᴇʀ Cᴜsᴛᴏᴍ TDs',
             'gofile': 'Gᴏғɪʟᴇ',
             'streamtape': 'Sᴛʀᴇᴀᴍᴛᴀᴘᴇ',
             }

async def get_user_settings(from_user, key=None, edit_type=None, edit_mode=None):
    user_id = from_user.id
    name = from_user.mention(style="html")
    buttons = ButtonMaker()
    thumbpath = f"Thumbnails/{user_id}.jpg"
    rclone_path = f'wcl/{user_id}.conf'
    user_dict = user_data.get(user_id, {})
    if key is None:
        buttons.ibutton("Uɴɪᴠᴇʀsᴀʟ Sᴇᴛᴛɪɴɢs ", f"userset {user_id} universal")
        buttons.ibutton("Mɪʀʀᴏʀ Sᴇᴛᴛɪɴɢs", f"userset {user_id} mirror")
        buttons.ibutton("Lᴇᴇᴄʜ Sᴇᴛᴛɪɴɢs", f"userset {user_id} leech")
        if user_dict and any(key in user_dict for key in list(fname_dict.keys())):
            buttons.ibutton("Rᴇsᴇᴛ Sᴇᴛᴛɪɴɢs", f"userset {user_id} reset_all")
        buttons.ibutton("❌", f"userset {user_id} close")

        text = BotTheme('USER_SETTING', NAME=name, ID=user_id, USERNAME=f'@{from_user.username}', LANG=Language.get(lc).display_name() if (lc := from_user.language_code) else "N/A", DC=from_user.dc_id)
        
        button = buttons.build_menu(1)
    elif key == 'universal':
        ytopt = 'Not Exists' if (val:=user_dict.get('yt_opt', config_dict.get('YT_DLP_OPTIONS', ''))) == '' else val
        buttons.ibutton(f"{'✅️' if ytopt != 'Not Exists' else ''} Yᴛ-ᴅʟᴘ Oᴘᴛɪᴏɴs", f"userset {user_id} yt_opt")
        u_sess = 'Exists' if user_dict.get('usess', False) else 'Not Exists'
        buttons.ibutton(f"{'✅️' if u_sess != 'Not Exists' else ''} Usᴇʀ Sᴇssɪᴏɴ", f"userset {user_id} usess")
        bot_pm = "Enabled" if user_dict.get('bot_pm', config_dict['BOT_PM']) else "Disabled"
        buttons.ibutton('Dɪsᴀʙʟᴇ Bᴏᴛ PM' if bot_pm == 'Enabled' else 'Eɴᴀʙʟᴇ Bᴏᴛ PM', f"userset {user_id} bot_pm")
        if config_dict['BOT_PM']:
            bot_pm = "Force Enabled"
        mediainfo = "Enabled" if user_dict.get('mediainfo', config_dict['SHOW_MEDIAINFO']) else "Disabled"
        buttons.ibutton('Dɪsᴀʙʟᴇ Mᴇᴅɪᴀɪɴғᴏ' if mediainfo == 'Enabled' else 'Eɴᴀʙʟᴇ Mᴇᴅɪᴀɪɴғᴏ', f"userset {user_id} mediainfo")
        if config_dict['SHOW_MEDIAINFO']:
            mediainfo = "Force Enabled"
        save_mode = "Sᴀᴠᴇ As Dᴜᴍᴘ" if user_dict.get('save_mode') else "Sᴀᴠᴇ As BᴏᴛPM"
        buttons.ibutton('Sᴀᴠᴇ As BᴏᴛPM' if save_mode == 'Sᴀᴠᴇ As Dᴜᴍᴘ' else 'Sᴀᴠᴇ As Dᴜᴍᴘ', f"userset {user_id} save_mode")
        dailytl = config_dict['DAILY_TASK_LIMIT'] or "∞"
        dailytas = user_dict.get('dly_tasks')[1] if user_dict and user_dict.get('dly_tasks') and user_id != OWNER_ID and config_dict['DAILY_TASK_LIMIT'] else config_dict['DAILY_TASK_LIMIT'] or "️∞" if user_id != OWNER_ID else "∞"
        if user_dict.get('dly_tasks', False):
            t = str(datetime.now() - user_dict['dly_tasks'][0]).split(':')
            lastused = f"{t[0]}h {t[1]}m {t[2].split('.')[0]}s ago"
        else: lastused = "Bot Not Used yet.."

        text = BotTheme('UNIVERSAL', NAME=name, YT=escape(ytopt), DT=f"{dailytas} / {dailytl}", LAST_USED=lastused, BOT_PM=bot_pm, MEDIAINFO=mediainfo, SAVE_MODE=save_mode, USESS=u_sess)
        buttons.ibutton("◀️", f"userset {user_id} back", "footer")
        buttons.ibutton("❌", f"userset {user_id} close", "footer")
        button = buttons.build_menu(2)
    elif key == 'mirror':
        buttons.ibutton("RCʟᴏɴᴇ", f"userset {user_id} rcc")
        rccmsg = "Exɪsᴛs" if await aiopath.exists(rclone_path) else "Nᴏᴛ Exɪsᴛs"
        dailytlup = get_readable_file_size(config_dict['DAILY_MIRROR_LIMIT'] * 1024**3) if config_dict['DAILY_MIRROR_LIMIT'] else "∞"
        dailyup = get_readable_file_size(await getdailytasks(user_id, check_mirror=True)) if config_dict['DAILY_MIRROR_LIMIT'] and user_id != OWNER_ID else "️∞"
        buttons.ibutton("Mɪʀʀᴏʀ Pʀᴇғɪx", f"userset {user_id} mprefix")
        mprefix = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('mprefix', config_dict.get('MIRROR_FILENAME_PREFIX', ''))) == '' else val

        buttons.ibutton("Mɪʀʀᴏʀ Sᴜғғɪx", f"userset {user_id} msuffix")
        msuffix = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('msuffix', config_dict.get('MIRROR_FILENAME_SUFFIX', ''))) == '' else val

        buttons.ibutton("Mɪʀʀᴏʀ Rᴇᴍɴᴀᴍᴇ", f"userset {user_id} mremname")
        mremname = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('mremname', config_dict.get('MIRROR_FILENAME_REMNAME', ''))) == '' else val

        ddl_serv = len(val) if (val := user_dict.get('ddl_servers', False)) else 0
        buttons.ibutton("DDL Sᴇʀᴠᴇʀs", f"userset {user_id} ddl_servers")

        tds_mode = "Eɴᴀʙʟᴇᴅ" if user_dict.get('td_mode', False) else "Dɪsᴀʙʟᴇᴅ"
        if not config_dict['USER_TD_MODE']:
            tds_mode = "Fᴏʀᴄᴇ Dɪsᴀʙʟᴇᴅ"

        user_tds = len(val) if (val := user_dict.get('user_tds', False)) else 0
        buttons.ibutton("Usᴇʀ TDs", f"userset {user_id} user_tds")

        text = BotTheme('MIRROR', NAME=name, RCLONE=rccmsg, DDL_SERVER=ddl_serv, DM=f"{dailyup} / {dailytlup}", MREMNAME=escape(mremname), MPREFIX=escape(mprefix),
                MSUFFIX=escape(msuffix), TMODE=tds_mode, USERTD=user_tds)

        buttons.ibutton("◀️", f"userset {user_id} back", "footer")
        buttons.ibutton("❌", f"userset {user_id} close", "footer")
        button = buttons.build_menu(2)
    elif key == 'leech':
        if user_dict.get('as_doc', False) or 'as_doc' not in user_dict and config_dict['AS_DOCUMENT']:
            ltype = "Dᴏᴄᴜᴍᴇɴᴛ"
            buttons.ibutton("Sᴇɴᴅ As Mᴇᴅɪᴀ", f"userset {user_id} doc")
        else:
            ltype = "Mᴇᴅɪᴀ"
            buttons.ibutton("Sᴇɴᴅ As Dᴏᴄᴜᴍᴇɴᴛ", f"userset {user_id} doc")

        dailytlle = get_readable_file_size(config_dict['DAILY_LEECH_LIMIT'] * 1024**3) if config_dict['DAILY_LEECH_LIMIT'] else "️∞"
        dailyll = get_readable_file_size(await getdailytasks(user_id, check_leech=True)) if config_dict['DAILY_LEECH_LIMIT'] and user_id != OWNER_ID else "∞"

        thumbmsg = "Exɪsᴛs" if await aiopath.exists(thumbpath) else "Nᴏᴛ Exɪsᴛs"
        buttons.ibutton(f"{'✅️' if thumbmsg == 'Exɪsᴛs' else ''} Tʜᴜᴍʙɴᴀɪʟ", f"userset {user_id} thumb")
        
        split_size = get_readable_file_size(config_dict['LEECH_SPLIT_SIZE']) + ' (Default)' if user_dict.get('split_size', '') == '' else get_readable_file_size(user_dict['split_size'])
        equal_splits = 'Enabled' if user_dict.get('equal_splits', config_dict.get('EQUAL_SPLITS')) else 'Dɪsᴀʙʟᴇᴅ'
        media_group = 'Enabled' if user_dict.get('media_group', config_dict.get('MEDIA_GROUP')) else 'Dɪsᴀʙʟᴇᴅ'
        buttons.ibutton(f"{'✅️' if user_dict.get('split_size') else ''} Lᴇᴇᴄʜ Sᴘʟɪᴛs", f"userset {user_id} split_size")

        lcaption = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('lcaption', config_dict.get('LEECH_FILENAME_CAPTION', ''))) == '' else val
        buttons.ibutton(f"{'✅️' if lcaption != 'Nᴏᴛ Exɪsᴛs' else ''} Lᴇᴇᴄʜ Cᴀᴘᴛɪᴏɴ", f"userset {user_id} lcaption")

        lprefix = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('lprefix', config_dict.get('LEECH_FILENAME_PREFIX', ''))) == '' else val
        buttons.ibutton(f"{'✅️' if lprefix != 'Nᴏᴛ Exɪsᴛs' else ''} Lᴇᴇᴄʜ Pʀᴇғɪx", f"userset {user_id} lprefix")

        lsuffix = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('lsuffix', config_dict.get('LEECH_FILENAME_SUFFIX', ''))) == '' else val
        buttons.ibutton(f"{'✅️' if lsuffix != 'Nᴏᴛ Exɪsᴛs' else ''} Lᴇᴇᴄʜ Sᴜғғɪx", f"userset {user_id} lsuffix")

        lremname = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('lremname', config_dict.get('LEECH_FILENAME_REMNAME', ''))) == '' else val
        buttons.ibutton(f"{'✅️' if lremname != 'Nᴏᴛ Exɪsᴛs' else ''} Lᴇᴇᴄʜ Rᴇᴍɴᴀᴍᴇ", f"userset {user_id} lremname")

        buttons.ibutton("Lᴇᴇᴄʜ Dᴜᴍᴘ", f"userset {user_id} ldump")
        ldump = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('ldump', '')) == '' else len(val)

        lmeta = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('lmeta', config_dict.get('METADATA', ''))) == '' else val
        buttons.ibutton(f"{'✅️' if lmeta != 'Nᴏᴛ Exɪsᴛs' else ''} Mᴇᴛᴀᴅᴀᴛᴀ", f"userset {user_id} lmeta")
                
        text = BotTheme('LEECH', NAME=name, DL=f"{dailyll} / {dailytlle}",
                LTYPE=ltype, THUMB=thumbmsg, SPLIT_SIZE=split_size,
                EQUAL_SPLIT=equal_splits, MEDIA_GROUP=media_group,
                LCAPTION=escape(lcaption), LPREFIX=escape(lprefix),
                LSUFFIX=escape(lsuffix), LDUMP=ldump, LREMNAME=escape(lremname), LMETA=escape(lmeta))

        buttons.ibutton("◀️", f"userset {user_id} back", "footer")
        buttons.ibutton("❌", f"userset {user_id} close", "footer")
        button = buttons.build_menu(2)
    elif key == "ddl_servers":
        ddl_serv, serv_list = 0, []
        if (ddl_dict := user_dict.get('ddl_servers', False)):
            for serv, (enabled, _) in ddl_dict.items():
                if enabled:
                    serv_list.append(serv)
                    ddl_serv += 1
        text = f"㊂ <b><u>{fname_dict[key]} Sᴇᴛᴛɪɴɢs :</u></b>\n\n" \
               f"➲ <b>Eɴᴀʙʟᴇᴅ DDL Sᴇʀᴠᴇʀ(s) :</b> <i>{ddl_serv}</i>\n\n" \
               f"➲ <b>Dᴇsᴄʀɪᴘᴛɪᴏɴ :</b> <i>{desp_dict[key][0]}</i>"
        for btn in ['gofile', 'streamtape']:
            buttons.ibutton(f"{'✅️' if btn in serv_list else ''} {fname_dict[btn]}", f"userset {user_id} {btn}")
        buttons.ibutton("◀️", f"userset {user_id} back mirror", "footer")
        buttons.ibutton("❌", f"userset {user_id} close", "footer")
        button = buttons.build_menu(2)
    elif edit_type:
        text = f"㊂ <b><u>{fname_dict[key]} Sᴇᴛᴛɪɴɢs :</u></b>\n\n"
        if key == 'rcc':
            set_exist = await aiopath.exists(rclone_path)
            text += f"➲ <b>RCʟᴏɴᴇ.Cᴏɴғ Fɪʟᴇ :</b> <i>{'' if set_exist else 'Not'} Exists</i>\n\n"
        elif key == 'thumb':
            set_exist = await aiopath.exists(thumbpath)
            text += f"➲ <b>Cᴜsᴛᴏᴍ Tʜᴜᴍʙɴᴀɪʟ :</b> <i>{'' if set_exist else 'Not'} Exists</i>\n\n"
        elif key == 'yt_opt':
            set_exist = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get('yt_opt', config_dict.get('YT_DLP_OPTIONS', ''))) == '' else val
            text += f"➲ <b>Yᴛ-Dʟᴘ Oᴘᴛɪᴏɴs :</b> <code>{escape(set_exist)}</code>\n\n"
        elif key == 'usess':
            set_exist = 'Exɪsᴛs' if user_dict.get('usess') else 'Nᴏᴛ Exɪsᴛs'
            text += f"➲ <b>{fname_dict[key]} :</b> <code>{set_exist}</code>\n➲ <b>Eɴᴄʀʏᴘᴛɪᴏɴ :</b> {'🔐' if set_exist else '🔓'}\n\n"
        elif key == 'split_size':
            set_exist = get_readable_file_size(config_dict['LEECH_SPLIT_SIZE']) + ' (Default)' if user_dict.get('split_size', '') == '' else get_readable_file_size(user_dict['split_size'])
            text += f"➲ <b>Lᴇᴇᴄʜ Sᴘʟɪᴛ Sɪᴢᴇ :</b> <i>{set_exist}</i>\n\n"
            if user_dict.get('equal_splits', False) or ('equal_splits' not in user_dict and config_dict['EQUAL_SPLITS']):
                buttons.ibutton("Dɪsᴀʙʟᴇ Eǫᴜᴀʟ Sᴘʟɪᴛs", f"userset {user_id} esplits", "header")
            else:
                buttons.ibutton("Eɴᴀʙʟᴇ Eǫᴜᴀʟ Sᴘʟɪᴛs", f"userset {user_id} esplits", "header")
            if user_dict.get('media_group', False) or ('media_group' not in user_dict and config_dict['MEDIA_GROUP']):
                buttons.ibutton("Dɪsᴀʙʟᴇ Mᴇᴅɪᴀ Gʀᴏᴜᴘ", f"userset {user_id} mgroup", "header")
            else:
                buttons.ibutton("Eɴᴀʙʟᴇ Mᴇᴅɪᴀ Gʀᴏᴜᴘ", f"userset {user_id} mgroup", "header")
        elif key in ['lprefix', 'lremname', 'lsuffix', 'lcaption', 'ldump', 'lmeta']:
            set_exist = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get(key, config_dict.get(f'LEECH_FILENAME_{key[1:].upper()}', ''))) == '' else val
            if set_exist != 'Nᴏᴛ Exɪsᴛs' and key == "ldump":
                set_exist = '\n\n' + '\n'.join([f"{index}. <b>{dump}</b> : <code>{ids}</code>" for index, (dump, ids) in enumerate(val.items(), start=1)])
            text += f"➲ <b>Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ {fname_dict[key]} :</b> {set_exist}\n\n"
        elif key in ['mprefix', 'mremname', 'msuffix']:
            set_exist = 'Nᴏᴛ Exɪsᴛs' if (val:=user_dict.get(key, config_dict.get(f'MIRROR_FILENAME_{key[1:].upper()}', ''))) == '' else val
            text += f"➲ <b>Mɪʀʀᴏʀ Fɪʟᴇɴᴀᴍᴇ {fname_dict[key]} :</b> {set_exist}\n\n"
        elif key in ['gofile', 'streamtape']:
            set_exist = 'Exɪsᴛs' if key in (ddl_dict:=user_dict.get('ddl_servers', {})) and ddl_dict[key][1] and ddl_dict[key][1] != '' else 'Nᴏᴛ Exɪsᴛs'
            ddl_mode = 'Eɴᴀʙʟᴇᴅ' if key in (ddl_dict:=user_dict.get('ddl_servers', {})) and ddl_dict[key][0] else 'Dɪsᴀʙʟᴇᴅ'
            text = f"➲ <b>Uᴘʟᴏᴀᴅ {fname_dict[key]} :</b> {ddl_mode}\n" \
                   f"➲ <b>{fname_dict[key]}'s API Key :</b> {set_exist}\n\n"
            buttons.ibutton('Dɪsᴀʙʟᴇ DDL' if ddl_mode == 'Eɴᴀʙʟᴇᴅ' else 'Eɴᴀʙʟᴇ DDL', f"userset {user_id} s{key}", "header")
        elif key == 'user_tds':
            set_exist = len(val) if (val:=user_dict.get(key, False)) else 'Not Exists'
            tds_mode = "Eɴᴀʙʟᴇᴅ" if user_dict.get('td_mode', False) else "Disabled"
            buttons.ibutton('Dɪsᴀʙʟᴇ UsᴇʀTDs' if tds_mode == 'Eɴᴀʙʟᴇᴅ' else 'Eɴᴀʙʟᴇ UsᴇʀTDs', f"userset {user_id} td_mode", "header")
            if not config_dict['USER_TD_MODE']:
                tds_mode = "Fᴏʀᴄᴇ Dɪsᴀʙʟᴇᴅ"
            text += f"➲ <b>Usᴇʀ TD Mᴏᴅᴇ :</b> {tds_mode}\n"
            text += f"➲ <b>{fname_dict[key]} :</b> {set_exist}\n\n"
        else: 
            return
        text += f"➲ <b>Dᴇsᴄʀɪᴘᴛɪᴏɴ :</b> <i>{desp_dict[key][0]}</i>"
        if not edit_mode:
            buttons.ibutton(f"Cʜᴀɴɢᴇ {fname_dict[key]}" if set_exist and set_exist != 'Not Exists' and (set_exist != get_readable_file_size(config_dict['LEECH_SPLIT_SIZE']) + ' (Default)') else f"Set {fname_dict[key]}", f"userset {user_id} {key} edit")
        else:
            text += '\n\n' + desp_dict[key][1]
            buttons.ibutton("Sᴛᴏᴘ Cʜᴀɴɢᴇ", f"userset {user_id} {key}")
        if set_exist and set_exist != 'Nᴏᴛ Exɪsᴛs' and (set_exist != get_readable_file_size(config_dict['LEECH_SPLIT_SIZE']) + ' (Default)'):
            if key == 'thumb':
                buttons.ibutton("Vɪᴇᴡ Tʜᴜᴍʙɴᴀɪʟ", f"userset {user_id} vthumb", "header")
            elif key == 'user_tds':
                buttons.ibutton('Sʜᴏᴡ UsᴇʀTDs', f"userset {user_id} show_tds", "header")
            buttons.ibutton("↻ Dᴇʟᴇᴛᴇ", f"userset {user_id} d{key}")
        buttons.ibutton("◀️", f"userset {user_id} back {edit_type}", "footer")
        buttons.ibutton("❌", f"userset {user_id} close", "footer")
        button = buttons.build_menu(2)
    return text, button


async def update_user_settings(query, key=None, edit_type=None, edit_mode=None, msg=None, sdirect=False):
    msg, button = await get_user_settings(msg.from_user if sdirect else query.from_user, key, edit_type, edit_mode)
    await editMessage(query if sdirect else query.message, msg, button)


async def user_settings(client, message):
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEtGzNmub75STO9jVh_xcnBhkXFr-GVpAACdQ8AAh4V8UuN549XMF_AnzUE")
    await asyncio.sleep(1)
    await sticker_message.delete()
    await send_react(message)
    if len(message.command) > 1 and (message.command[1] == '-s' or message.command[1] == '-set'):
        set_arg = message.command[2].strip() if len(message.command) > 2 else None
        msg = await sendMessage(message, '<i>Fᴇᴛᴄʜɪɴɢ Sᴇᴛᴛɪɴɢs...</i>', photo='IMAGES')
        if set_arg and (reply_to := message.reply_to_message):
            if message.from_user.id != reply_to.from_user.id:
                return await editMessage(msg, '<i>Rᴇᴘʟʏ ᴛᴏ Yᴏᴜʀ Oᴡɴ Mᴇssᴀɢᴇ ғᴏʀ Sᴇᴛᴛɪɴɢ ᴠɪᴀ Aʀɢs Dɪʀᴇᴄᴛʟʏ</i>')
            if set_arg in ['lprefix', 'lsuffix', 'lremname', 'lcaption', 'ldump', 'yt_opt', 'lmeta'] and reply_to.text:
                return await set_custom(client, reply_to, msg, set_arg, True)
            elif set_arg == 'thumb' and reply_to.media:
                return await set_thumb(client, reply_to, msg, set_arg, True)
        await editMessage(msg, '''㊂ <b><u>Aᴠᴀɪʟᴀʙʟᴇ Fʟᴀɢs :</u></b>
>> Rᴇᴘʟʏ ᴛᴏ ᴛʜᴇ Vᴀʟᴜᴇ ᴡɪᴛʜ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ᴀʀɢ ʀᴇsᴘᴇᴄᴛɪᴠᴇʟʏ ᴛᴏ sᴇᴛ ᴅɪʀᴇᴄᴛʟʏ ᴡɪᴛʜᴏᴜᴛ ᴏᴘᴇɴɪɴɢ USᴇᴛ.

➲ <b>Cᴜsᴛᴏᴍ Tʜᴜᴍʙɴᴀɪʟ :</b>
    /cmd -s thumb
➲ <b>Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Pʀᴇғɪx :</b>
    /cmd -s lprefix
➲ <b>Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Sᴜғғɪx :</b>
    /cmd -s lsuffix
➲ <b>Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Rᴇᴍɴᴀᴍᴇ :</b>
    /cmd -s lremname
➲ <b>Lᴇᴇᴄʜ Mᴇᴛᴀᴅᴀᴛᴀ Tᴇxᴛ :</b>
    /cmd -s lmeta
➲ <b>Lᴇᴇᴄʜ Fɪʟᴇɴᴀᴍᴇ Cᴀᴘᴛɪᴏɴ :</b>
    /cmd -s lcaption
➲ <b>Yᴛ-Dʟᴘ Oᴘᴛɪᴏɴs :</b>
    /cmd -s yt_opt
➲ <b>Lᴇᴇᴄʜ Usᴇʀ Dᴜᴍᴘ :</b>
    /cmd -s ldump''')
    else:
        from_user = message.from_user
        handler_dict[from_user.id] = False
        msg, button = await get_user_settings(from_user)
        await sendMessage(message, msg, button, 'IMAGES')


async def set_custom(client, message, pre_event, key, direct=False):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    value = message.text
    return_key = 'leech'
    n_key = key
    user_dict = user_data.get(user_id, {})
    if key in ['gofile', 'streamtape']:
        ddl_dict = user_dict.get('ddl_servers', {})
        mode, api = ddl_dict.get(key, [False, ""])
        if key == "gofile" and not await Gofile.is_goapi(value):
            value = ""
        ddl_dict[key] = [mode, value]
        value = ddl_dict
        n_key = 'ddl_servers'
        return_key = 'ddl_servers'
    elif key == 'user_tds':
        user_tds = user_dict.get(key, {})
        for td_item in value.split('\n'):
            if td_item == '':
                continue
            split_ck = td_item.split()
            td_details = td_item.rsplit(maxsplit=(2 if split_ck[-1].startswith('http') and not is_gdrive_link(split_ck[-1]) else 1 if len(split_ck[-1]) > 15 else 0))
            if td_details[0] in list(categories_dict.keys()):
                continue
            for title in list(user_tds.keys()):
                if td_details[0].casefold() == title.casefold():
                    del user_tds[title]
            if len(td_details) > 1:
                if is_gdrive_link(td_details[1].strip()):
                    td_details[1] = GoogleDriveHelper.getIdFromUrl(td_details[1])
                if await sync_to_async(GoogleDriveHelper().getFolderData, td_details[1]):
                    user_tds[td_details[0]] = {'drive_id': td_details[1],'index_link': td_details[2].rstrip('/') if len(td_details) > 2 else ''}
        value = user_tds
        return_key = 'mirror'
    elif key == 'ldump':
        ldumps = user_dict.get(key, {})
        for dump_item in value.split('\n'):
            if dump_item == '':
                continue
            dump_info = dump_item.rsplit(maxsplit=(1 if dump_item.split()[-1].startswith(('-100', '@')) else 0))
            if dump_info[0] in list(ldumps.keys()):
                continue
            for title in list(ldumps.keys()):
                if dump_info[0].casefold() == title.casefold():
                    del ldumps[title]
            if len(dump_info) > 1 and (dump_chat := await chat_info(dump_info[1])):
                ldumps[dump_info[0]] = dump_chat.id
        value = ldumps
    elif key in ['yt_opt', 'usess']:
        if key == 'usess':
            password = Fernet.generate_key()
            try:
                await deleteMessage(await (await sendCustomMsg(message.from_user.id, f"<u><b>Decryption Key:</b></u> \n┃\n┃ <code>{password.decode()}</code>\n┃\n┖ <b>Note:</b> <i>Keep this Key Securely, this is not Stored in Bot and Access Key to use your Session...</i>")).pin(both_sides=True))
                encrypt_sess = Fernet(password).encrypt(value.encode())
                value = encrypt_sess.decode()
            except Exception:
                value = ""
        return_key = 'universal'
    update_user_ldata(user_id, n_key, value)
    await deleteMessage(message)
    await update_user_settings(pre_event, key, return_key, msg=message, sdirect=direct)
    if DATABASE_URL:
        await DbManger().update_user_data(user_id)


async def set_thumb(client, message, pre_event, key, direct=False):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    path = "Thumbnails/"
    if not await aiopath.isdir(path):
        await mkdir(path)
    photo_dir = await message.download()
    des_dir = ospath.join(path, f'{user_id}.jpg')
    await sync_to_async(Image.open(photo_dir).convert("RGB").save, des_dir, "JPEG")
    await aioremove(photo_dir)
    update_user_ldata(user_id, 'thumb', des_dir)
    await deleteMessage(message)
    await update_user_settings(pre_event, key, 'leech', msg=message, sdirect=direct)
    if DATABASE_URL:
        await DbManger().update_user_doc(user_id, 'thumb', des_dir)


async def add_rclone(client, message, pre_event):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    path = f'{getcwd()}/wcl/'
    if not await aiopath.isdir(path):
        await mkdir(path)
    des_dir = ospath.join(path, f'{user_id}.conf')
    await message.download(file_name=des_dir)
    update_user_ldata(user_id, 'rclone', f'wcl/{user_id}.conf')
    await deleteMessage(message)
    await update_user_settings(pre_event, 'rcc', 'mirror')
    if DATABASE_URL:
        await DbManger().update_user_doc(user_id, 'rclone', des_dir)


async def leech_split_size(client, message, pre_event):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    sdic = ['b', 'kb', 'mb', 'gb']
    value = message.text.strip()
    slice = -2 if value[-2].lower() in ['k', 'm', 'g'] else -1
    out = value[slice:].strip().lower()
    if out in sdic:
        value = min((float(value[:slice].strip()) * 1024**sdic.index(out)), MAX_SPLIT_SIZE)
    update_user_ldata(user_id, 'split_size', int(round(value)))
    await deleteMessage(message)
    await update_user_settings(pre_event, 'split_size', 'leech')
    if DATABASE_URL:
        await DbManger().update_user_data(user_id)


async def event_handler(client, query, pfunc, rfunc, photo=False, document=False):
    user_id = query.from_user.id
    handler_dict[user_id] = True
    start_time = time()

    async def event_filter(_, __, event):
        if photo:
            mtype = event.photo
        elif document:
            mtype = event.document
        else:
            mtype = event.text
        user = event.from_user or event.sender_chat
        return bool(user.id == user_id and event.chat.id == query.message.chat.id and mtype)
        
    handler = client.add_handler(MessageHandler(
        pfunc, filters=create(event_filter)), group=-1)
    while handler_dict[user_id]:
        await sleep(0.5)
        if time() - start_time > 60:
            handler_dict[user_id] = False
            await rfunc()
    client.remove_handler(*handler)


@new_thread
async def edit_user_settings(client, query):
    from_user = query.from_user
    user_id = from_user.id
    message = query.message
    data = query.data.split()
    thumb_path = f'Thumbnails/{user_id}.jpg'
    rclone_path = f'wcl/{user_id}.conf'
    user_dict = user_data.get(user_id, {})
    if user_id != int(data[1]):
        await query.answer("Not Yours!", show_alert=True)
    elif data[2] in ['universal', 'mirror', 'leech']:
        await query.answer()
        await update_user_settings(query, data[2])
    elif data[2] == "doc":
        update_user_ldata(user_id, 'as_doc', not user_dict.get('as_doc', False))
        await query.answer()
        await update_user_settings(query, 'leech')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] == 'vthumb':
        handler_dict[user_id] = False
        await query.answer()
        buttons = ButtonMaker()
        buttons.ibutton('Cʟᴏsᴇ', f'wzmlx {user_id} close')
        await sendMessage(message, from_user.mention, buttons.build_menu(1), thumb_path)
        await update_user_settings(query, 'thumb', 'leech')
    elif data[2] == 'show_tds':
        handler_dict[user_id] = False
        user_tds = user_dict.get('user_tds', {})
        msg = f'➲ <b><u>Usᴇʀ TD(s) Dᴇᴛᴀɪʟs</u></b>\n\n<b>Tᴏᴛᴀʟ UsᴇʀTD(s) :</b> {len(user_tds)}\n\n'
        for index_no, (drive_name, drive_dict) in enumerate(user_tds.items(), start=1):
            msg += f'{index_no}: <b>Nᴀᴍᴇ:</b> <code>{drive_name}</code>\n'
            msg += f"  <b>Dʀɪᴠᴇ Iᴅ:</b> <code>{drive_dict['drive_id']}</code>\n"
            msg += f"  <b>Iɴᴅᴇx Lɪɴᴋ:</b> <code>{ind_url if (ind_url := drive_dict['index_link']) else 'Nᴏᴛ Pʀᴏᴠɪᴅᴇᴅ'}</code>\n\n"
        try:
            await sendCustomMsg(user_id, msg)
            await query.answer('Usᴇʀ TDs Sᴜᴄᴄᴇssғᴜʟʟʏ Sᴇɴᴅ ɪɴ ʏᴏᴜʀ PM', show_alert=True)
        except Exception:
            await query.answer('Sᴛᴀʀᴛ ᴛʜᴇ Bᴏᴛ ɪɴ PM (Pʀɪᴠᴀᴛᴇ) ᴀɴᴅ Tʀʏ Aɢᴀɪɴ', show_alert=True)
        await update_user_settings(query, 'user_tds', 'mirror')
    elif data[2] == "dthumb":
        handler_dict[user_id] = False
        if await aiopath.exists(thumb_path):
            await query.answer()
            await aioremove(thumb_path)
            update_user_ldata(user_id, 'thumb', '')
            await update_user_settings(query, 'thumb', 'leech')
            if DATABASE_URL:
                await DbManger().update_user_doc(user_id, 'thumb')
        else:
            await query.answer("Oʟᴅ Sᴇᴛᴛɪɴɢs", show_alert=True)
            await update_user_settings(query, 'leech')
    elif data[2] == 'thumb':
        await query.answer()
        edit_mode = len(data) == 4
        await update_user_settings(query, data[2], 'leech', edit_mode)
        if not edit_mode: return
        pfunc = partial(set_thumb, pre_event=query, key=data[2])
        rfunc = partial(update_user_settings, query, data[2], 'leech')
        await event_handler(client, query, pfunc, rfunc, True)
    elif data[2] in ['yt_opt', 'usess']:
        await query.answer()
        edit_mode = len(data) == 4
        await update_user_settings(query, data[2], 'universal', edit_mode)
        if not edit_mode: return
        pfunc = partial(set_custom, pre_event=query, key=data[2])
        rfunc = partial(update_user_settings, query, data[2], 'universal')
        await event_handler(client, query, pfunc, rfunc)
    elif data[2] in ['dyt_opt', 'dusess']:
        handler_dict[user_id] = False
        await query.answer()
        update_user_ldata(user_id, data[2][1:], '')
        await update_user_settings(query, data[2][1:], 'universal')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] in ['bot_pm', 'mediainfo', 'save_mode', 'td_mode']:
        handler_dict[user_id] = False
        if data[2] == 'save_mode' and not user_dict.get(data[2], False) and not user_dict.get('ldump'):
            return await query.answer("Sᴇᴛ Usᴇʀ Dᴜᴍᴘ ғɪʀsᴛ ᴛᴏ Cʜᴀɴɢᴇ Sᴀᴠᴇ Msɢ Mᴏᴅᴇ !", show_alert=True)
        elif data[2] == 'bot_pm' and (config_dict['BOT_PM'] or config_dict['SAFE_MODE']) or data[2] == 'mediainfo' and config_dict['SHOW_MEDIAINFO'] or data[2] == 'td_mode' and not config_dict['USER_TD_MODE']:
            mode_up = "Disabled" if data[2] == 'td_mode' else "Enabled"
            return await query.answer(f"Fᴏʀᴄᴇ {mode_up}! Cᴀɴ'ᴛ Aʟᴛᴇʀ Sᴇᴛᴛɪɴɢs", show_alert=True)
        if data[2] == 'td_mode' and not user_dict.get('user_tds', False):
            return await query.answer("Sᴇᴛ UsᴇʀTD ғɪʀsᴛ ᴛᴏ Eɴᴀʙʟᴇ Usᴇʀ TD Mᴏᴅᴇ !", show_alert=True)
        await query.answer()
        update_user_ldata(user_id, data[2], not user_dict.get(data[2], False))
        if data[2] in ['td_mode']:
            await update_user_settings(query, 'user_tds', 'mirror')
        else:
            await update_user_settings(query, 'universal')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] == 'split_size':
        await query.answer()
        edit_mode = len(data) == 4
        await update_user_settings(query, data[2], 'leech', edit_mode)
        if not edit_mode: return
        pfunc = partial(leech_split_size, pre_event=query)
        rfunc = partial(update_user_settings, query, data[2], 'leech')
        await event_handler(client, query, pfunc, rfunc)
    elif data[2] == 'dsplit_size':
        handler_dict[user_id] = False
        await query.answer()
        update_user_ldata(user_id, 'split_size', '')
        await update_user_settings(query, 'split_size', 'leech')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] == 'esplits':
        handler_dict[user_id] = False
        await query.answer()
        update_user_ldata(user_id, 'equal_splits', not user_dict.get('equal_splits', False))
        await update_user_settings(query, 'leech')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] == 'mgroup':
        handler_dict[user_id] = False
        await query.answer()
        update_user_ldata(user_id, 'media_group', not user_dict.get('media_group', False))
        await update_user_settings(query, 'leech')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] in ['sgofile', 'sstreamtape', 'dgofile', 'dstreamtape']:
        handler_dict[user_id] = False
        ddl_dict = user_dict.get('ddl_servers', {})
        key = data[2][1:]
        mode, api = ddl_dict.get(key, [False, ""])
        if data[2][0] == 's':
            if not mode and api == '':
                return await query.answer('Sᴇᴛ API ᴛᴏ Eɴᴀʙʟᴇ DDL Sᴇʀᴠᴇʀ', show_alert=True)
            ddl_dict[key] = [not mode, api]
        elif data[2][0] == 'd':
            ddl_dict[key] = [mode, '']
        await query.answer()
        update_user_ldata(user_id, 'ddl_servers', ddl_dict)
        await update_user_settings(query, key, 'ddl_servers')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] == 'rcc':
        await query.answer()
        edit_mode = len(data) == 4
        await update_user_settings(query, data[2], 'mirror', edit_mode)
        if not edit_mode: return
        pfunc = partial(add_rclone, pre_event=query)
        rfunc = partial(update_user_settings, query, data[2], 'mirror')
        await event_handler(client, query, pfunc, rfunc, document=True)
    elif data[2] == 'drcc':
        handler_dict[user_id] = False
        if await aiopath.exists(rclone_path):
            await query.answer()
            await aioremove(rclone_path)
            update_user_ldata(user_id, 'rclone', '')
            await update_user_settings(query, 'rcc', 'mirror')
            if DATABASE_URL:
                await DbManger().update_user_doc(user_id, 'rclone')
        else:
            await query.answer("Old Settings", show_alert=True)
            await update_user_settings(query)
    elif data[2] in ['ddl_servers', 'user_tds', 'gofile', 'streamtape']:
        handler_dict[user_id] = False
        await query.answer()
        edit_mode = len(data) == 4
        await update_user_settings(query, data[2], 'mirror' if data[2] in ['ddl_servers', 'user_tds'] else 'ddl_servers', edit_mode)
        if not edit_mode: return
        pfunc = partial(set_custom, pre_event=query, key=data[2])
        rfunc = partial(update_user_settings, query, data[2], 'mirror' if data[2] in ['ddl_servers', 'user_tds'] else "ddl_servers")
        await event_handler(client, query, pfunc, rfunc)
    elif data[2] in ['lprefix', 'lsuffix', 'lremname', 'lcaption', 'ldump', 'mprefix', 'msuffix', 'mremname', 'lmeta']:
        handler_dict[user_id] = False
        await query.answer()
        edit_mode = len(data) == 4
        return_key = 'leech' if data[2][0] == 'l' else 'mirror'
        await update_user_settings(query, data[2], return_key, edit_mode)
        if not edit_mode: return
        pfunc = partial(set_custom, pre_event=query, key=data[2])
        rfunc = partial(update_user_settings, query, data[2], return_key)
        await event_handler(client, query, pfunc, rfunc)
    elif data[2] in ['dlprefix', 'dlsuffix', 'dlremname', 'dlcaption', 'dldump', 'dlmeta']:
        handler_dict[user_id] = False
        await query.answer()
        update_user_ldata(user_id, data[2][1:], {} if data[2] == 'dldump' else '')
        await update_user_settings(query, data[2][1:], 'leech')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] in ['dmprefix', 'dmsuffix', 'dmremname', 'duser_tds']:
        handler_dict[user_id] = False
        await query.answer()
        update_user_ldata(user_id, data[2][1:], {} if data[2] == 'duser_tds' else '')
        if data[2] == 'duser_tds':
            update_user_ldata(user_id, 'td_mode', False)
        await update_user_settings(query, data[2][1:], 'mirror')
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
    elif data[2] == 'back':
        handler_dict[user_id] = False
        await query.answer()
        setting = data[3] if len(data) == 4 else None
        await update_user_settings(query, setting)
    elif data[2] == 'reset_all':
        handler_dict[user_id] = False
        await query.answer()
        buttons = ButtonMaker()
        buttons.ibutton('Yᴇs', f"userset {user_id} reset_now y")
        buttons.ibutton('Nᴏ', f"userset {user_id} reset_now n")
        buttons.ibutton("❌", f"userset {user_id} close", "footer")
        await editMessage(message, 'Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ Rᴇsᴇᴛ Sᴇᴛᴛɪɴɢs ?', buttons.build_menu(2))
    elif data[2] == 'reset_now':
        handler_dict[user_id] = False
        if data[3] == 'n':
            return await update_user_settings(query)
        if await aiopath.exists(thumb_path):
            await aioremove(thumb_path)
        if await aiopath.exists(rclone_path):
            await aioremove(rclone_path)
        await query.answer()
        update_user_ldata(user_id, None, None)
        await update_user_settings(query)
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
            await DbManger().update_user_doc(user_id, 'thumb')
            await DbManger().update_user_doc(user_id, 'rclone')
    elif data[2] == 'user_del':
        user_id = int(data[3])
        await query.answer()
        thumb_path = f'Thumbnails/{user_id}.jpg'
        rclone_path = f'wcl/{user_id}.conf'
        if await aiopath.exists(thumb_path):
            await aioremove(thumb_path)
        if await aiopath.exists(rclone_path):
            await aioremove(rclone_path)
        update_user_ldata(user_id, None, None)
        if DATABASE_URL:
            await DbManger().update_user_data(user_id)
            await DbManger().update_user_doc(user_id, 'thumb')
            await DbManger().update_user_doc(user_id, 'rclone')
        await editMessage(message, f'Data Reset for {user_id}')
    else:
        handler_dict[user_id] = False
        await query.answer()
        await deleteMessage(message.reply_to_message)
        await deleteMessage(message)
        
async def send_users_settings(client, message):
    text = message.text.split(maxsplit=1)
    userid = text[1] if len(text) > 1 else None
    if userid and not userid.isdigit():
        userid = None
    elif (reply_to := message.reply_to_message) and reply_to.from_user and not reply_to.from_user.is_bot:
        userid = reply_to.from_user.id
    if not userid:
        msg = f'<u><b>Total Users / Chats Data Saved :</b> {len(user_data)}</u>'
        buttons = ButtonMaker()
        buttons.ibutton("❌", f"userset {message.from_user.id} close")
        button = buttons.build_menu(1)
        for user, data in user_data.items():
            msg += f'\n\n<code>{user}</code>:'
            if data:
                for key, value in data.items():
                    if key in ['token', 'time', 'ddl_servers', 'usess']:
                        continue
                    msg += f'\n<b>{key}</b>: <code>{escape(str(value))}</code>'
            else:
                msg += "\nUser's Data is Empty!"
        if len(msg.encode()) > 4000:
            with BytesIO(str.encode(msg)) as ofile:
                ofile.name = 'users_settings.txt'
                await sendFile(message, ofile)
        else:
            await sendMessage(message, msg, button)
    elif int(userid) in user_data:
        msg = f'{(await user_info(userid)).mention(style="html")} ( <code>{userid}</code> ):'
        if data := user_data[int(userid)]:
            buttons = ButtonMaker()
            buttons.ibutton("Dᴇʟᴇᴛᴇ Dᴀᴛᴀ", f"userset {message.from_user.id} user_del {userid}")
            buttons.ibutton("❌", f"userset {message.from_user.id} close")
            button = buttons.build_menu(1)
            for key, value in data.items():
                if key in ['token', 'time', 'ddl_servers', 'usess']:
                    continue
                msg += f'\n<b>{key}</b>: <code>{escape(str(value))}</code>'
        else:
            msg += '\nThis User has not Saved anything.'
            button = None
        await sendMessage(message, msg, button)
    else:
        await sendMessage(message, f'{userid} have not saved anything..')


bot.add_handler(MessageHandler(send_users_settings, filters=command(
    BotCommands.UsersCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(user_settings, filters=command(
    BotCommands.UserSetCommand) & CustomFilters.authorized_uset))
bot.add_handler(CallbackQueryHandler(edit_user_settings, filters=regex("^userset")))
