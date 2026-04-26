from aiogram.types import BotCommand, BotCommandScopeAllGroupChats

private_commands = [
    BotCommand(command="/start", description="Почати роботу з ботом"),
    BotCommand(command="/menu", description="Повернутись до головного меню"),
]

group_commands = [
    BotCommand(command="/spell", description="Пошук закляття: /spell <назва>"),
]
