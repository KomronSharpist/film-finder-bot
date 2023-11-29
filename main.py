import asyncio
import json
import logging
import re
from aiogram import Dispatcher
from aiogram.enums import ChatMemberStatus
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, types

logging.basicConfig(level=logging.INFO)
bot = Bot(token="6919625489:AAGRw9EzaogxU7Hubfk1qhGldhNs1iNhfTo")
# bot = Bot(token="5701012090:AAGRTr0XVls7yrfcyX1XaP1btLV4D9mWYjY")
dp = Dispatcher()
chanel_add_session = {}
film_delete_session = {}
film_add_session = {}
chanel_control_session = {}
admin_sessions = {}
logging.basicConfig(level=logging.INFO)
admin_userIds = {1052097431: "𝙺𝚘𝚖𝚛𝚘𝚗", 6723202097: "Brad_Thompson"}
channel_usernames = []

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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    channel_unsubscribed = []
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
        await message.answer("• Botdan foydalanish uchun avval kanalga obuna bo’ling va <b>Tekshirish</b> tugmasini bosing!",
                             reply_markup=builder.as_markup(), parse_mode="HTML")
        return
    else:
        keyboard = types.ReplyKeyboardRemove()
        await message.answer("✌️Assalomu Aleykum\n👨‍🔧Men Sizga kod orqali kino topib beraman!\nBuning uchun botga kino kodini yuborsangiz bo'lgani.", reply_markup=keyboard)

@dp.message(Command("admin"))
async def cmd_start_admin(message: types.Message):
    if message.from_user.id in admin_userIds.keys():
        admin_sessions[message.from_user.id] = True
        kb = [
            [
                types.KeyboardButton(text="Kino qoshish 🎬"),
                types.KeyboardButton(text="Kinolar royxati 🎬")
            ],
            [
                types.KeyboardButton(text="Kino o'chirish ❌"),
                types.KeyboardButton(text="Kanal qo'shish ➕")
            ],
            [types.KeyboardButton(text="Orqaga qaytish 🔙")],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(f"Admin panelga xush kelibsiz. Menuni tanlang!", reply_markup=keyboard)

async def check_subcription(message: types.Message):
    user_id = message.from_user.id
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
        return True
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text

    if await check_subcription(message):
        if user_message == "Orqaga qaytish  🔙" or user_message == "Bekor qilish ❌" :
            if user_id in chanel_control_session:
                del chanel_control_session[user_id]
            if user_id in chanel_add_session:
                del chanel_add_session[user_id]
            kb = [
                [
                    types.KeyboardButton(text="Kino qoshish 🎬"),
                    types.KeyboardButton(text="Kinolar royxati 🎬")
                ],
                [types.KeyboardButton(text="Kino o'chirish ❌")],
                [types.KeyboardButton(text="Kanal qo'shish ➕")],
                [types.KeyboardButton(text="Orqaga qaytish 🔙")],
            ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer(f"Admin panelga xush kelibsiz. Menuni tanlang!", reply_markup=keyboard)
        elif user_id in chanel_control_session:
            await chanel_control_session_service(message)
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
                caption = entry.get('caption')

                if entry['media_type'] == 'photo':
                    await bot.send_photo(chat_id=message.from_user.id, photo=file_id, caption=caption, parse_mode="HTML")
                elif entry['media_type'] == 'video':
                    await bot.send_video(chat_id=message.from_user.id, video=file_id, caption=caption, parse_mode="HTML")

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

    except FileNotFoundError:
        await bot.send_message(message.from_user.id, "Hozircha hech qanday filmlar yo'q❗️")


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
        await message.answer("Kinoni tashlang 🎬",reply_markup=keyboard)
    if user_message == "Kanal qo'shish ➕":
        chanel_control_session[user_id] = True
        kb = [
            [
                types.KeyboardButton(text="Kino qoshish 🎬"),
                types.KeyboardButton(text="Kinolar royxati 🎬")
            ],
            [
                types.KeyboardButton(text="Kino o'chirish ❌"),
                types.KeyboardButton(text="Kanal qo'shish ➕")
            ],
            [types.KeyboardButton(text="Orqaga qaytish 🔙")],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            "Kanal qo'shish ➕",
            reply_markup=keyboard)
    if user_message == "Orqaga qaytish 🔙":
        del admin_sessions[user_id]
        keyboard = types.ReplyKeyboardRemove()
        await message.answer(
            "✌️Assalomu Aleykum\n👨‍🔧Men Sizga kod orqali kino topib beraman!\nBuning uchun botga kino kodini yuborsangiz bo'lgani.",
            reply_markup=keyboard)


async def get_list_films(message: types.Message):
    json_filename = 'file_data.json'
    try:
        with open(json_filename, 'r') as json_file:
            data = json.load(json_file)

        if not isinstance(data, list) or not data:
            await bot.send_message(message.from_user.id, "Hozircha hech qanday filmlar yo'q❗️")
            return

        films_list = "\n".join([f"Kino:\n\ncode: {entry['code']}\n   caption: {entry.get('caption', 'No caption')}\n\n" for entry in data])
        await bot.send_message(message.from_user.id, films_list, parse_mode="HTML")

    except FileNotFoundError:
        await bot.send_message(message.from_user.id, "Hozircha hech qanday filmlar yo'q❗️")

async def film_control_session_service(message: types.Message):
    user_id = message.from_user.id
    user_message= message.text

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
        else: await message.answer("Iltimos kanal nomini tog'ri kiriting!")
    if user_message == "Kanal qoshish ➕":
        chanel_add_session[user_id] = True
        await message.answer("Qoshmoqchi bolgan kanalingizni jonating. Misol : @kanal", )
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
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            await callback.answer("")
            await callback.message.answer("✌️Assalomu Aleykum\n👨‍🔧Men Sizga kod orqali kino topib beraman!\nBuning uchun botga kino kodini yuborsangiz bo'lgani.", parse_mode="HTML")

async def set_default_commands():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Qayta ishga tushurish"),
    ])

async def main():
    await set_default_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(bot.close())