import asyncio
import json
import logging
import re
from collections import defaultdict
from datetime import datetime, date, timedelta, time, timezone
from aiogram import Dispatcher
from aiogram.enums import ChatMemberStatus
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, types
import time

logging.basicConfig(level=logging.INFO)
# bot = Bot(token="6919625489:AAGRw9EzaogxU7Hubfk1qhGldhNs1iNhfTo") # test
bot = Bot(token="6931061308:AAG4a6WYw2Qsm6sdnLzVG-ccFj_KAxT-0Hc")
dp = Dispatcher()
chanel_add_session = {}
chanel_control_session = {}
admin_control_session = {}
admin_add_session = {}
chat_sessions = {}
admin_sessions = {}
owner_sessions = {}
user_reload_messages = {}
send_message_session = {}
inline_keyboard_session = {}
add_inline_keyboard_session = {}
logging.basicConfig(level=logging.INFO)
admin_userIds = {1052097431: "𝙺𝚘𝚖𝚛𝚘𝚗", 6723202097: "Admin"}
today = datetime.now().date()
ownerId = [6723202097, 1052097431]
user_request_counts = defaultdict(int)
user_last_request = {}
reklam = ""
reklamBuilder = InlineKeyboardBuilder()
video_file_id = 0
chat_id = 0
user_states = {}
channel_usernames = []
sended_users = []
unsended_users = []
last_response_time = {}
film_delete_session = {}
film_add_session = {}

try:
    with open('all_users.json', 'r') as file:
        all_users = json.load(file)
except FileNotFoundError:
    all_users = []

try:
    with open('inactive_users.json', 'r') as file:
        inactive_users = json.load(file)
except FileNotFoundError:
    inactive_users = []

try:
    with open('active_users.json', 'r') as file:
        active_users = json.load(file)
except FileNotFoundError:
    active_users = []

try:
    with open('today_active_users.json', 'r') as file:
        today_active_users = json.load(file)
except FileNotFoundError:
    today_active_users = []

try:
    with open('today_logined_users.json', 'r') as file:
        today_logined_users = json.load(file)
except FileNotFoundError:
    today_logined_users = []


try:
    with open('week_logined_users.json', 'r') as file:
        week_logined_users = json.load(file)
except FileNotFoundError:
    week_logined_users = []


async def is_subscribed(user_id, channel_username):
    try:
        member = await bot.get_chat_member(channel_username, user_id)
        desired_statuses = {
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
        }
        if member.status in desired_statuses:
            return True
    except Exception as e:
        return False


async def periodic_user_check():
    while True:
        now_utc = datetime.now(timezone.utc)
        utc_plus_5 = timedelta(hours=5)
        now = now_utc + utc_plus_5
        next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), timezone.utc)
        time_until_midnight = (next_midnight - now).total_seconds()

        hours, remainder = divmod(time_until_midnight, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Keyingi yangilanishgacha: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        await asyncio.sleep(time_until_midnight)

        today_active_users.clear()
        today_logined_users.clear()
        with open('today_logined_users.json', 'w') as file:
            json.dump(today_logined_users, file)
        with open('today_active_users.json', 'w') as file:
            json.dump(today_active_users, file)

async def periodic_user_week_check():
    while True:
        now_utc = datetime.now(timezone.utc)
        utc_plus_5 = timedelta(hours=5)
        now = now_utc + utc_plus_5

        days_until_next_sunday = (6 - now.weekday()) % 7
        next_sunday_midnight = datetime.combine(now.date() + timedelta(days=days_until_next_sunday), datetime.min.time(), timezone.utc)
        time_until_next_sunday = (next_sunday_midnight - now).total_seconds()

        hours, remainder = divmod(time_until_next_sunday, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Keyingi yangilanishgacha: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        await asyncio.sleep(time_until_next_sunday)

        week_logined_users.clear()
        with open('week_logined_users.json', 'w') as file:
            json.dump(week_logined_users, file)

def get_duplicates():
    seen = set()
    duplicates = set()
    for item in today_active_users:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    if user_id in user_states.keys():
        user_states[user_id]['awaiting_response'] = False
    else:
        user_states[user_id] = {'awaiting_response': False}
    channel_unsubscribed = []
    if user_id in admin_control_session:
        del admin_control_session[user_id]
    if user_id in admin_add_session:
        del admin_add_session[user_id]

    if user_id in chanel_control_session:
        del chanel_control_session[user_id]
    if user_id in chanel_add_session:
        del chanel_add_session[user_id]

    for channel_username in channel_usernames:
        if await is_subscribed(user_id, channel_username):
            continue
        else:
            channel_unsubscribed.append(channel_username)
    builder = InlineKeyboardBuilder()
    for channel in channel_unsubscribed:
        builder.add(types.InlineKeyboardButton(text=f"{channel}", url=f"https://t.me/{channel[1:]}"))
        builder.adjust(1, 1)
    if channel_unsubscribed:
        builder.add(types.InlineKeyboardButton(text=f"Tekshirish ✅", callback_data="checkSubscription"))
        builder.adjust(1, 1)
        await message.answer(
            "• Botdan foydalanish uchun avval kanalga obuna bo’ling va <b>Tekshirish</b> tugmasini bosing!",
            reply_markup=builder.as_markup(), parse_mode="HTML")
        return
    else:
        keyboard = types.ReplyKeyboardRemove()
        await message.answer(
            "✌️Assalomu Aleykum\n👨‍🔧Men Sizga kod orqali kino topib beraman!\nBuning uchun botga kino kodini yuborsangiz bo'lgani.",
            reply_markup=keyboard)

@dp.message(Command("myid"))
async def cmd_start(message: types.Message):
    if message.chat.type != 'private':
        return
    keyboard = types.ReplyKeyboardRemove()
    await message.answer(f"Sizning ID raqamingiz: {message.from_user.id}", reply_markup=keyboard)


@dp.message(Command("admin"))
async def cmd_start_admin(message: types.Message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    user = message.from_user
    if user_id in admin_userIds.keys():
        admin_sessions[user_id] = True
        if user_id in ownerId:
            owner_sessions[user_id] = True
            kb = [
                [
                    types.KeyboardButton(text="Kino qoshish 🎬"),
                    types.KeyboardButton(text="Kinolar royxati 🎬")
                ],
                [
                    types.KeyboardButton(text="Kino o'chirish ❌"),
                    types.KeyboardButton(text="Kanal qo'shish ➕")
                ],
                [
                    types.KeyboardButton(text="Xabar yuborish ✉️"),
                    types.KeyboardButton(text="Statistika 📊")
                ],
                [types.KeyboardButton(text="Orqaga qaytish 🔙")],
            ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer(f"Admin panelga xush kelibsiz. Menuni tanlang!", reply_markup=keyboard)
        elif user_id in admin_userIds.keys():
            kb = [
                [
                    types.KeyboardButton(text="Xabar yuborish ✉️"),
                    types.KeyboardButton(text="Statistika 📊")
                ],
                [types.KeyboardButton(text="Kanal qo'shish ➕")],
                [types.KeyboardButton(text="Orqaga qaytish 🔙")],
            ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer(f"Admin panelga xush kelibsiz. Menuni tanlang!", reply_markup=keyboard)


async def check_subcription(message: types.Message):
    user_id = message.from_user.id
    user = message.from_user

    channel_unsubscribed = []
    for channel_username in channel_usernames:
        if await is_subscribed(user_id, channel_username):
            continue
        else:
            channel_unsubscribed.append(channel_username)
    builder = InlineKeyboardBuilder()
    for channel in channel_unsubscribed:
        builder.add(types.InlineKeyboardButton(text=f"{channel}", url=f"https://t.me/{channel[1:]}"))
        builder.adjust(1, 1)
    if channel_unsubscribed:
        builder.add(types.InlineKeyboardButton(text=f"Tekshirish ✅", callback_data="checkSubscription"))
        builder.adjust(1, 1)
        await message.answer(
            "• Botdan foydalanish uchun avval kanalga obuna bo’ling va <b>Tekshirish</b> tugmasini bosing!",
            reply_markup=builder.as_markup(), parse_mode="HTML")
        return
    elif len(channel_unsubscribed) == 0:
        if user_id not in today_logined_users and user_id not in all_users:
            today_logined_users.append(user_id)
            with open('today_logined_users.json', 'w') as file:
                json.dump(today_logined_users, file)
        if user_id not in week_logined_users and user_id not in all_users:
            week_logined_users.append(user_id)
            with open('week_logined_users.json', 'w') as file:
                json.dump(week_logined_users, file)
        today_active_users.append(user_id)
        with open('today_active_users.json', 'w') as file:
            json.dump(today_active_users, file)
        if user_id not in all_users:
            all_users.append(user_id)
            with open('all_users.json', 'w') as file:
                json.dump(all_users, file)
        if user_id not in active_users:
            active_users.append(user_id)
            with open('active_users.json', 'w') as file:
                json.dump(active_users, file)
        if user_id in all_users:
            if user_id in inactive_users:
                inactive_users.remove(user_id)
                with open('inactive_users.json', 'w') as file:
                    json.dump(inactive_users, file)
        return True


@dp.message()
async def handle_message(message: types.Message):
    if message.chat.type != 'private':
        return
    global new_api_key, last_api_key_update, video_file_id, reklam, reklamBuilder
    user_id = message.from_user.id
    user_message = message.text
    if user_id not in user_states.keys():
        user_states[user_id] = {'awaiting_response': False}

    if await check_subcription(message):
        if user_message == "Orqaga qaytish  🔙" or user_message == "Bekor qilish ❌":
            reklam = ""
            reklamBuilder = InlineKeyboardBuilder()
            if user_id in send_message_session:
                del send_message_session[user_id]
            if user_id in add_inline_keyboard_session:
                del add_inline_keyboard_session[user_id]
            if user_id in inline_keyboard_session:
                del inline_keyboard_session[user_id]
            if user_id in admin_control_session:
                del admin_control_session[user_id]
            if user_id in admin_add_session:
                del admin_add_session[user_id]
            if user_id in chanel_control_session:
                del chanel_control_session[user_id]
            if user_id in chanel_add_session:
                del chanel_add_session[user_id]
            if user_id in ownerId:
                owner_sessions[user_id] = True
                kb = [
                    [
                        types.KeyboardButton(text="Kino qoshish 🎬"),
                        types.KeyboardButton(text="Kinolar royxati 🎬")
                    ],
                    [
                        types.KeyboardButton(text="Kino o'chirish ❌"),
                        types.KeyboardButton(text="Kanal qo'shish ➕")
                    ],
                    [
                        types.KeyboardButton(text="Xabar yuborish ✉️"),
                        types.KeyboardButton(text="Statistika 📊")
                    ],
                    [types.KeyboardButton(text="Orqaga qaytish 🔙")],
                ]
                keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                await message.answer(f"Admin panelga xush kelibsiz. Menuni tanlang!", reply_markup=keyboard)
            elif user_id in admin_userIds.keys():
                kb = [
                    [
                        types.KeyboardButton(text="Statistika 📊")
                    ],
                    [types.KeyboardButton(text="Kanal qo'shish ➕")],
                    [types.KeyboardButton(text="Orqaga qaytish 🔙")],
                ]
                keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                await message.answer(f"Admin panelga xush kelibsiz. Menuni tanlang!", reply_markup=keyboard)
        elif user_id in admin_control_session:
            await admin_control_session_service(message)
        elif user_id in inline_keyboard_session:
            if user_message == "Qo'shish ✅":
                add_inline_keyboard_session[user_id] = True
                kb = [
                    [
                        types.KeyboardButton(text="Bekor qilish ❌"),
                    ]
                ]
                keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                await message.answer(
                    "Kanal nomi*Kanal sslikasi\nKanal nomi*Kanal sslikasi\n...\n\nIltimos shu ko`rinishda kiriting",
                    reply_markup=keyboard)
            elif user_message == "Tashlab o'tish ❌":
                if isinstance(reklam, types.Message) and reklam.video:
                    video = reklam.video
                    caption = reklam.caption

                    await bot.send_video(
                        chat_id=user_id,
                        video=video.file_id,
                        caption=caption,
                        disable_notification=True,
                        reply_markup=reklamBuilder.as_markup(),
                        parse_mode="HTML"
                    )
                elif isinstance(reklam, types.Message):
                    await bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=reklam.chat.id,
                        message_id=reklam.message_id,
                        reply_markup=reklamBuilder.as_markup(),
                        parse_mode="HTML"
                    )
                kb = [
                    [
                        types.KeyboardButton(text="Yuborish ✅"),
                        types.KeyboardButton(text="Bekor qilish ❌"),
                    ]
                ]
                keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                await message.answer(
                    "Xabaringiz to'g'rimi? Agarda to'g'ri bo'lsa \"Yuborish ✅\" tugmasini bosing aks holda \"Bekor qilish ❌\"ni bosing",
                    reply_markup=keyboard)
            elif user_message == "Yuborish ✅":
                if user_id in ownerId:
                    owner_sessions[user_id] = True
                    del inline_keyboard_session[user_id]
                    kb = [
                        [
                            types.KeyboardButton(text="Kino qoshish 🎬"),
                            types.KeyboardButton(text="Kinolar royxati 🎬")
                        ],
                        [
                            types.KeyboardButton(text="Kino o'chirish ❌"),
                            types.KeyboardButton(text="Kanal qo'shish ➕")
                        ],
                        [
                            types.KeyboardButton(text="Xabar yuborish ✉️"),
                            types.KeyboardButton(text="Statistika 📊")
                        ],
                        [types.KeyboardButton(text="Orqaga qaytish 🔙")],
                    ]
                    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                    await message.answer(f"Admin panelga xush kelibsiz. Menuni tanlang!", reply_markup=keyboard)
                elif user_id in admin_userIds.keys():
                    kb = [
                        [
                            types.KeyboardButton(text="Xabar yuborish ✉️"),
                            types.KeyboardButton(text="Statistika 📊")
                        ],
                        [types.KeyboardButton(text="Kanal qo'shish ➕")],
                        [types.KeyboardButton(text="Orqaga qaytish 🔙")],
                    ]
                    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                    await message.answer(f"Admin panelga xush kelibsiz. Menuni tanlang!", reply_markup=keyboard)
                del send_message_session[message.from_user.id]
                await send_message_controller(message)
            elif user_id in add_inline_keyboard_session:
                keyboards = user_message.split("\n")
                for keyboard in keyboards:
                    name = keyboard.split("*")[0]
                    url = keyboard.split("*")[1]
                    reklamBuilder.add(types.InlineKeyboardButton(text=f"{name}", url=f"{url}"))
                    reklamBuilder.adjust(1, 1)
                if isinstance(reklam, types.Message) and reklam.video:
                    video = reklam.video
                    caption = reklam.caption

                    await bot.send_video(
                        chat_id=user_id,
                        video=video.file_id,
                        caption=caption,
                        disable_notification=True,
                        reply_markup=reklamBuilder.as_markup(),
                        parse_mode="HTML"
                    )
                elif isinstance(reklam, types.Message):
                    await bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=reklam.chat.id,
                        message_id=reklam.message_id,
                        reply_markup=reklamBuilder.as_markup(),
                        parse_mode="HTML"
                    )
                kb = [
                    [
                        types.KeyboardButton(text="Yuborish ✅"),
                        types.KeyboardButton(text="Bekor qilish ❌"),
                    ]
                ]
                keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                await message.answer(
                    "Xabaringiz to'g'rimi? Agarda to'g'ri bo'lsa \"Yuborish ✅\" tugmasini bosing aks holda \"Bekor qilish ❌\"ni bosing",
                    reply_markup=keyboard)
        elif user_id in send_message_session:
            await send_message_service(message)
        elif user_id in chanel_control_session:
            await chanel_control_session_service(message)
        elif user_message == "Ertangi kunga o'tish ✅":
            today_logined_users.clear()
            today_active_users.clear()
            with open('today_logined_users.json', 'w') as file:
                json.dump(today_logined_users, file)
            with open('today_active_users.json', 'w') as file:
                json.dump(today_active_users, file)
            await cmd_start_admin(message)
        elif user_id in film_add_session:
            await film_control_session_service(message)
        elif user_id in film_delete_session:
            await delete_film_by_code(message)
        elif user_id in admin_sessions:
            await admin_sessions_service(message)
        else:
            await get_film_by_code(message)


async def get_film_by_code(message: types.Message):
    json_filename = 'file_data.json'
    try:
        with open(json_filename, 'r') as json_file:
            data = json.load(json_file)

        if not isinstance(data, list):
            await bot.send_message(message.from_user.id, "Bunaqa kod mavjud emas❗️")
            return

        code_to_search = message.text
        matching_entries = [entry for entry in data if 'code' in entry and entry['code'] == code_to_search]

        if matching_entries:
            for entry in matching_entries:
                file_id = entry.get('media_file')
                raw_caption = entry.get('caption').replace('\\n', '\n')

                caption = raw_caption.encode('utf-8').decode('unicode-escape')

                if entry['media_type'] == 'photo':
                    await bot.send_photo(chat_id=message.from_user.id, photo=file_id, caption=caption,
                                         parse_mode="HTML")
                elif entry['media_type'] == 'video':
                    await bot.send_video(chat_id=message.from_user.id, video=file_id, caption=caption,
                                         parse_mode="HTML")

            return
        else:
            await bot.send_message(message.from_user.id, "Bunaqa kod mavjud emas❗️")

    except FileNotFoundError:
        await bot.send_message(message.from_user.id, "Bunaqa kod mavjud emas❗️")


async def delete_film_by_code(message: types.Message):
    json_filename = 'file_data.json'
    try:
        with open(json_filename, 'r') as json_file:
            data = json.load(json_file)

        if not isinstance(data, list) or not data:
            await bot.send_message(message.from_user.id, "Hozircha hech qanday filmlar yo'q❗️")
            del film_delete_session[message.from_user.id]
            return

        code_to_delete = message.text
        updated_data = [entry for entry in data if 'code' in entry and entry['code'] != code_to_delete]

        if len(updated_data) < len(data):
            with open(json_filename, 'w') as json_file:
                json.dump(updated_data, json_file)

            await bot.send_message(message.from_user.id, "Film o'chirildi✅")
            del film_delete_session[message.from_user.id]
        else:
            await bot.send_message(message.from_user.id, "Bunaqa kod bilan film topilmadi❗️")
            del film_delete_session[message.from_user.id]

    except FileNotFoundError:
        await bot.send_message(message.from_user.id, "Hozircha hech qanday filmlar yo'q❗️")
        del film_delete_session[message.from_user.id]


async def admin_control_session_service(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text
    if user_message == "Adminlar royxati 📄":
        builder = InlineKeyboardBuilder()
        for item in list(admin_userIds.items()):
            builder.add(types.InlineKeyboardButton(text=f"{item[0]}", callback_data=f"nothing"))
            builder.add(types.InlineKeyboardButton(text=f"{item[1]}", callback_data=f"nothing"))
            builder.add(types.InlineKeyboardButton(text=f"🗑", callback_data=f"admin_delete_{item[0]}"))
            builder.adjust(3, 3)
        await message.answer(
            f"Adminlar royxati 📄",
            reply_markup=builder.as_markup())
    elif user_id in admin_add_session:
        del admin_add_session[user_id]
        userid = user_message.split(" ")
        admin_userIds[int(userid[0])] = userid[1]
        await message.answer("Admin qoshildi", )
    if user_message == "Admin qoshish ➕":
        admin_add_session[user_id] = True
        await message.answer("Admin qoshish ➕ uchun uning ID sini va Ismini yozing. Misol : 2479323 Ismi", )


async def get_list_films(message: types.Message):
    json_filename = 'file_data.json'
    try:
        with open(json_filename, 'r') as json_file:
            data = json.load(json_file)

        if not isinstance(data, list) or not data:
            await bot.send_message(message.from_user.id, "Hozircha hech qanday filmlar yo'q❗️")
            return

        films_per_message = 10  # Set the number of films per message
        films_chunks = [data[i:i + films_per_message] for i in range(0, len(data), films_per_message)]

        for chunk in films_chunks:
            films_list = "\n".join(
                [f"Kino:\n\ncode: {entry['code']}\n   caption: {entry.get('caption', 'No caption')}\n\n" for entry in chunk])
            await bot.send_message(message.from_user.id, films_list, parse_mode="HTML")

    except FileNotFoundError:
        await bot.send_message(message.from_user.id, "Hozircha hech qanday filmlar yo'q❗️")


async def film_control_session_service(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text

    if message.photo:
        media_type = 'photo'
        media_file = message.photo[-1].file_id
    elif message.video:
        media_type = 'video'
        media_file = message.video.file_id
    elif user_message == "Orqaga qaytish 🔙":
        del film_add_session[user_id]
        await cmd_start_admin(message)

    caption = message.caption
    code_pattern = re.compile(r'#\d+')
    code_match = code_pattern.search(caption)
    if code_match:
        code = code_match.group()
        caption = caption.replace(code, '')
        code = code.replace('#', '')
    else:
        code = None

    json_filename = 'file_data.json'
    try:
        with open(json_filename, 'r') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        existing_data = []

    encoded_caption = caption.encode('unicode-escape').decode('utf-8')

    new_entry = {
        'media_type': media_type,
        'media_file': media_file,
        'caption': encoded_caption,
        'code': code,
    }

    existing_data.append(new_entry)
    with open(json_filename, 'w') as json_file:
        json.dump(existing_data, json_file)

    await message.answer(f"Saqlandi", parse_mode="HTML")
    del film_add_session[user_id]


async def admin_sessions_service(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text
    if user_message == "Kino o'chirish ❌":
        await message.answer("Kinoni raqamini tashalang ")
        film_delete_session[user_id] = True
    if user_message == "Kinolar royxati 🎬":
        await get_list_films(message)
    if user_message == "Kino qoshish 🎬":
        film_add_session[user_id] = True
        kb = []
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Kinoni tashlang 🎬", reply_markup=keyboard)
    if user_message == "Kanal qo'shish ➕":
        chanel_control_session[user_id] = True
        kb = [
            [
                types.KeyboardButton(text="Kanal qoshish ➕"),
                types.KeyboardButton(text="Kanallar royxati 📄"),
            ],
            [types.KeyboardButton(text="Orqaga qaytish  🔙")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            "Kanal qo'shish ➕",
            reply_markup=keyboard)
    if user_message == "Ertangi kunga otish 🔄" and user_id in ownerId:
        kb = [
            [types.KeyboardButton(text="Ertangi kunga o'tish ✅")],
            [types.KeyboardButton(text="Orqaga qaytish  🔙")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            "Rostdan ham keyingi kunga o'tmoqchimisiz?",
            reply_markup=keyboard)
    if user_message == "Xabar yuborish ✉️":
        send_message_session[user_id] = True
        kb = [
            [types.KeyboardButton(text="Orqaga qaytish  🔙")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(f"Marhamat xabaringizni yuborishingiz mumkin", reply_markup=keyboard)
    if user_message == "Admin boshqaruvi 👤" and user_id in ownerId:
        admin_control_session[user_id] = True
        kb = [
            [
                types.KeyboardButton(text="Admin qoshish ➕"),
                types.KeyboardButton(text="Adminlar royxati 📄"),
            ],
            [types.KeyboardButton(text="Orqaga qaytish  🔙")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            "Admin boshqaruvi 👤",
            reply_markup=keyboard)
    if user_message == "Statistika 📊":
        await message.answer(f"📊 Jami a'zolar soni: {len(all_users)}\n"
                             f"📈 Aktiv a'zolar soni: {len(active_users)}\n"
                             f"📊 Bugungi ishlatganlar: {len(get_duplicates())}\n"
                             f"📉 Block qilganlar soni: {len(inactive_users)}\n"
                             f"📊 Bugungi a'zolar: {len(today_logined_users)}\n"
                             f"📊 Haftalik a'zolar: {len(week_logined_users)}")
    if user_message == "Kanal qo'shish ➕":
        chanel_control_session[user_id] = True
        kb = [
            [
                types.KeyboardButton(text="Kanal qoshish ➕"),
                types.KeyboardButton(text="Kanallar royxati 📄"),
            ],
            [types.KeyboardButton(text="Orqaga qaytish  🔙")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            "Kanal qo'shish ➕",
            reply_markup=keyboard)
    if user_message == "Orqaga qaytish 🔙":
        if user_id in owner_sessions:
            del owner_sessions[user_id]
        del admin_sessions[user_id]
        keyboard = types.ReplyKeyboardRemove()
        await message.answer(
            "✌️Assalomu Aleykum\n👨‍🔧Men Sizga kod orqali kino topib beraman!\nBuning uchun botga kino kodini yuborsangiz bo'lgani.",
            parse_mode="HTML", reply_markup=keyboard)


async def send_message_service(message: types.Message):
    global reklam
    reklam = message
    kb = [
        [
            types.KeyboardButton(text="Qo'shish ✅"),
            types.KeyboardButton(text="Tashlab o'tish ❌"),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Xabaringiz saqlandi. Xabar tagiga keyboard reklama qo'shasizmi?", reply_markup=keyboard)
    inline_keyboard_session[message.from_user.id] = True


async def chanel_control_session_service(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text
    if user_message == "Kanallar royxati 📄":
        builder = InlineKeyboardBuilder()
        for item in channel_usernames:
            builder.add(types.InlineKeyboardButton(text=f"{item}", callback_data=f"nothing"))
            builder.add(types.InlineKeyboardButton(text=f"🗑", callback_data=f"channel_delete_{item}"))
            builder.adjust(2, 2)
        await message.answer(
            f"Siz qoshgan kanallar lar royxati",
            reply_markup=builder.as_markup())
    elif user_id in chanel_add_session:
        if user_message.startswith("@"):
            del chanel_add_session[user_id]
            channel_usernames.append(f"{user_message}")
            await message.answer("Kanal qoshildi", )
        else:
            await message.answer("Iltimos kanal nomini tog'ri kiriting!")
    if user_message == "Kanal qoshish ➕":
        chanel_add_session[user_id] = True
        await message.answer("Qoshmoqchi bolgan kanalingizni jonating. Misol : @kanal", )


async def send_video_message(user_id, video, caption, counter):
    try:
        await bot.send_video(
            chat_id=user_id,
            video=video.file_id,
            caption=caption,
            disable_notification=True,
            reply_markup=reklamBuilder.as_markup(),
            parse_mode="HTML"
        )
        print(f"{user_id} jonatildi, {len(all_users) - counter} qoldi ")
        sended_users.append(user_id)
        if user_id in inactive_users:
            active_users.append(user_id)
            inactive_users.remove(user_id)
            with open('inactive_users.json', 'w') as file:
                json.dump(inactive_users, file)
            with open('active_users.json', 'w') as file:
                json.dump(active_users, file)
    except Exception as e:
        print(f"{user_id} jonatilmadi, {len(all_users) - counter} qoldi ")
        unsended_users.append(user_id)
        if user_id in active_users:
            active_users.remove(user_id)
            inactive_users.append(user_id)
            with open('inactive_users.json', 'w') as file:
                json.dump(inactive_users, file)
            with open('active_users.json', 'w') as file:
                json.dump(active_users, file)


async def send_copy_message(user_id, counter, reklam):
    try:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=reklam.chat.id,
            message_id=reklam.message_id,
            reply_markup=reklamBuilder.as_markup(),
            parse_mode="HTML"
        )
        print(f"{user_id} jonatildi, {len(all_users) - counter} qoldi ")
        sended_users.append(user_id)
        if user_id in inactive_users:
            active_users.append(user_id)
            inactive_users.remove(user_id)
            with open('inactive_users.json', 'w') as file:
                json.dump(inactive_users, file)
            with open('active_users.json', 'w') as file:
                json.dump(active_users, file)
    except Exception as e:
        print(f"{user_id} jonatilmadi, {len(all_users) - counter} qoldi ")
        unsended_users.append(user_id)
        if user_id in active_users:
            active_users.remove(user_id)
            inactive_users.append(user_id)
            with open('inactive_users.json', 'w') as file:
                json.dump(inactive_users, file)
            with open('active_users.json', 'w') as file:
                json.dump(active_users, file)


async def send_message_controller(message: types.Message):
    global reklam
    start_time = datetime.now()
    counter = 0
    if isinstance(reklam, types.Message):
        video = reklam.video
        caption = reklam.caption

        for user_id in all_users:
            counter += 1
            if reklam.video:
                await send_video_message(user_id, video, caption, counter)
            else:
                await send_copy_message(user_id, counter, reklam)

    end_time = datetime.now()
    execution_time = end_time - start_time
    total_seconds = execution_time.total_seconds()
    minutes, seconds = divmod(total_seconds, 60)
    time_string = f"{int(minutes)} daqiqa {int(seconds)} sekund vaqt oralig'ida yuborildi."

    await message.answer(
        f"Xabaringiz yuborildi ✅\n\nYuborilmaganlar soni: {len(unsended_users)}\nYuborilganlar soni: {len(sended_users)}\n{time_string}"
    )


@dp.callback_query(lambda callback: callback.data.startswith("admin_delete_"))
async def admin_controller(callback: types.CallbackQuery):
    if callback.data.startswith("admin_delete_"):
        user_id = callback.data.split("_")
        admin = admin_userIds[int(user_id[2])]

        if admin:
            del admin_userIds[int(user_id[2])]
            builder = InlineKeyboardBuilder()
            for item in list(admin_userIds.items()):
                builder.add(types.InlineKeyboardButton(text=f"{item[0]}", callback_data=f"nothing"))
                builder.add(types.InlineKeyboardButton(text=f"{item[1]}", callback_data=f"nothing"))
                builder.add(types.InlineKeyboardButton(text=f"🗑", callback_data=f"admin_delete_{item[0]}"))
                builder.adjust(3, 3)
            await callback.message.answer(f"Adminlar royxati 📄", reply_markup=builder.as_markup())
            await callback.answer(f"Deleting admin: {admin}", show_alert=True)
        else:
            await callback.answer("Admin not found.", show_alert=True)


@dp.callback_query(lambda callback: callback.data.startswith("channel_delete_"))
async def channel_controller(callback: types.CallbackQuery):
    if callback.data.startswith("channel_delete_"):
        channel_name = callback.data.split("@")[1]
        if f"@{channel_name}" in channel_usernames:
            channel_usernames.remove(f"@{channel_name}")
            builder = InlineKeyboardBuilder()
            for item in channel_usernames:
                builder.add(types.InlineKeyboardButton(text=f"{item}", callback_data=f"nothing"))
                builder.add(types.InlineKeyboardButton(text=f"🗑", callback_data=f"channel_delete_{item}"))
                builder.adjust(2, 2)
            await callback.message.answer(f"Kanallar royxati 📄", reply_markup=builder.as_markup())
            await callback.answer(f"Deleting channel: {channel_name}", show_alert=True)
        else:
            await callback.answer("Chanel not found.", show_alert=True)


@dp.callback_query(lambda callback: callback.data.startswith("checkSubscription"))
async def channel_controller(callback: types.CallbackQuery):
    if callback.data.startswith("checkSubscription"):
        user_id = callback.from_user.id
        channel_unsubscribed = []
        for channel_username in channel_usernames:
            if await is_subscribed(user_id, channel_username):
                continue
            else:
                channel_unsubscribed.append(channel_username)
        builder = InlineKeyboardBuilder()
        for channel in channel_unsubscribed:
            builder.add(types.InlineKeyboardButton(text=f"{channel}", url=f"https://t.me/{channel[1:]}"))
            builder.adjust(1, 1)
        if channel_unsubscribed:
            await callback.answer("• Botdan foydalanish uchun avval kanalga obuna bo’ling.")
            return
        else:
            if user_id not in today_logined_users and user_id not in all_users:
                today_logined_users.append(user_id)
                with open('today_logined_users.json', 'w') as file:
                    json.dump(today_logined_users, file)
            if user_id not in week_logined_users and user_id not in all_users:
                week_logined_users.append(user_id)
                with open('week_logined_users.json', 'w') as file:
                    json.dump(week_logined_users, file)
            today_active_users.append(user_id)
            with open('today_active_users.json', 'w') as file:
                json.dump(today_active_users, file)
            if user_id not in all_users:
                all_users.append(user_id)
                with open('all_users.json', 'w') as file:
                    json.dump(all_users, file)
            if user_id not in active_users:
                active_users.append(user_id)
                with open('active_users.json', 'w') as file:
                    json.dump(active_users, file)
            if user_id in all_users and user_id in inactive_users:
                inactive_users.remove(user_id)
                with open('inactive_users.json', 'w') as file:
                    json.dump(inactive_users, file)
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            await callback.answer("")
            await callback.message.answer("✌️Assalomu Aleykum\n👨‍🔧Men Sizga kod orqali kino topib beraman!\nBuning uchun botga kino kodini yuborsangiz bo'lgani.", parse_mode="HTML")


async def set_default_commands():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Qayta ishga tushurish"),
        types.BotCommand(command="information", description="Foydalanish qo'llanmasi"),
    ])


async def main():
    await set_default_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.create_task(periodic_user_check())
    loop.create_task(periodic_user_week_check())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()

        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()