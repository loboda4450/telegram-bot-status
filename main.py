import asyncio
import datetime
from typing import Optional, Any

from telethon import TelegramClient
import logging

from yaml import safe_load
from asyncio import run, get_event_loop
from pydantic import BaseModel

with open("config.yml", 'r') as f:
    config = safe_load(f)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config['log_level'])
logger = logging.getLogger(__name__)


class botInstance(BaseModel):
    active: bool
    id: str
    timeout: int
    query: str
    message: dict
    inline: dict
    message_sent: Optional[Any]
    data: Optional[dict]


def init_bots(bot_configs: dict):
    return [botInstance(**bot_configs[bot]) for bot in bot_configs.keys()]


async def main(config):
    async with TelegramClient(**config['telethon_settings']) as client:
        await client.start()
        bots = init_bots(config['bots'])

        # data[event.from_id.user_id]['answered_on'] = datetime.datetime.timestamp(event.message.date)

        for bot in bots:
            if bot.active:
                bot.message_sent = await client.send_message(bot.id, message=bot.query)
                # entity = await client.get_entity(bots[bot]['id'])
                bot.data = {
                    'expected_replies': bot.message['alive_replies'],
                    'waiting_until': datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(5)),
                    'answered_on': None,
                }

        await asyncio.sleep(5)

        # for bot in bots:
        #     if bot.message_sent:
        #         if datetime.datetime.timestamp(datetime.datetime.now()) < bot.data['waiting_until']:
        #             if bot.message[]
        #
        await client.run_until_disconnected()


if __name__ == '__main__':
    get_event_loop().run_until_complete(main(config=config))
