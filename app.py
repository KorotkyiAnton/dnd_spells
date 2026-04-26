import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

from scripts.import_spells import import_spells_if_empty
from common.bot_commands_list import private_commands, group_commands
from database.engine import session_maker, create_db
from handlers.common import common_router
from handlers.unknown_message import unknown_router
from middlewares.db import DataBaseSession
from middlewares.messages import MessagesMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = "/webhook"
PORT = int(os.getenv("PORT", 8080))

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()

dp.message.middleware(MessagesMiddleware())
dp.callback_query.middleware(MessagesMiddleware())
dp.include_router(common_router)
dp.include_router(unknown_router)


async def on_startup() -> None:
    await create_db()
    await import_spells_if_empty()
    await bot.set_webhook(f"{WEBHOOK_HOST}{WEBHOOK_PATH}")
    await bot.set_my_commands(commands=private_commands, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=group_commands, scope=BotCommandScopeAllGroupChats())
    logging.info("Bot started — webhook set to %s%s", WEBHOOK_HOST, WEBHOOK_PATH)


async def on_shutdown() -> None:
    await bot.delete_webhook()
    logging.info("Bot stopped — webhook deleted")


def main() -> None:
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=PORT)


main()
