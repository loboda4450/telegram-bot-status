import asyncio
import datetime
from typing import Dict, List

from influx_line_protocol import Metric, MetricCollection
from telethon import TelegramClient
import logging

from telethon.events import NewMessage
from telethon.tl.types import Message
from yaml import safe_load
from asyncio import run, get_event_loop
from pydantic import BaseModel

with open("config.yml", 'r') as f:
    config = safe_load(f)

bots = config['bots']
data = {}
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config['log_level'])
logger = logging.getLogger(__name__)


class botInstance(BaseModel):
    active: bool
    id: str
    timeout: int
    query: str
    message: Dict[List[str]]
    inline: Dict[List[str]]


def init_bots(bot_configs: dict):
    return [botInstance(**bot_configs[bot]) for bot in bot_configs.keys()]


async def checker(event: Message):
    if data[event.from_id.user_id]:
        if data[event.from_id.user_id]['message_id'] == event.reply_to_msg_id:
            if data[event.from_id.user_id]['waiting_until'] > datetime.datetime.timestamp(event.message.date):
                return True
    else:
        return False


async def main(config):
    async with TelegramClient(**config['telethon_settings']) as client:
        await client.start()

        @client.on(event=NewMessage(incoming=True, from_users=(bots[bot]['id'] for bot in bots),
                                    func=checker))  # 100% sure i can do it better XD
        async def handler(event):
            data[event.from_id.user_id]['answered_on'] = datetime.datetime.timestamp(event.message.date)

        for bot in bots:
            if bots[bot]['active']:
                message = await client.send_message(bots[bot]['id'], message=bots[bot]['query'])
                entity = await client.get_entity(bots[bot]['id'])
                data[entity.id] = {
                    'message_id': message.id,
                    'expected_replies': bots[bot]['message']['alive_replies'],
                    'waiting_until': datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(5)),
                    'answered_on': None,
                }

        await client.run_until_disconnected()


if __name__ == '__main__':
    get_event_loop().run_until_complete(main(config=config))
