from telethon import TelegramClient, events, types
from database import get_user_by_tg_id, get_text, get_user_ids, priority
from config import api_id, api_hash
from aiogram_app import bot
import aiogram;

client = TelegramClient('tg_session', api_id, api_hash, system_version='4.16.30-vxCUSTOM')
async def check_chat_type(chat_id):
    entity = await client.get_entity(chat_id)
    if isinstance(entity, types.User):
        print("Личный чат")
        return 0
    elif isinstance(entity, types.Chat):
        print("Группа")
        return 1
    elif isinstance(entity, types.Channel):
        print("Канал")
        return 2

@client.on(events.NewMessage)
async def my_event_handler(event):
    ids = get_user_ids()
    for id in ids:
        await client.get_dialogs()
        event_msg = event.message
        text_msg = event_msg.message
        peer_id = event_msg.chat_id
        entity_type = await check_chat_type(peer_id)
        if entity_type == 2 and get_user_by_tg_id(id[0]) is not None:
            for elem in get_text(id[0]):
                if elem["text"] in text_msg:
                    try:
                        channel_id = event_msg.peer_id.channel_id
                        link = f"https://t.me/c/{channel_id}/{event_msg.id}"
                        text = f'<a href="{link}">Сообщение из канала</a>\nТекст из поста: {text_msg}'
                        if elem["priority"]:
                            msg = await bot.send_message(id[0], text, parse_mode=aiogram.types.ParseMode.HTML)
                            await bot.pin_chat_message(id[0], msg.message_id)
                        else:
                            await bot.send_message(id[0], text, parse_mode=aiogram.types.ParseMode.HTML)
                    except ValueError as e:
                        print(e)


print("Telethon App Started")
client.start()
client.run_until_disconnected()
