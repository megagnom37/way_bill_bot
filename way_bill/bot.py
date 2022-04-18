from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from way_bill.app.handler import Handler
from way_bill.app.utils.filters import AvailableUsers
from way_bill.app.config import config


class WayBillBot:
    COMMANDS = [
        types.bot_command.BotCommand(
            command="/start", 
            description="Начать работу с ботом"
        ),
    ]

    async def init_bot(self):
        logger.info('Initializing bot...')
        
        self._bot = Bot(token=config['way_bill_telegram_token'])
        await self._bot.set_my_commands(self.COMMANDS)
        
        self._dp = Dispatcher(self._bot, storage=MemoryStorage())
        self._dp.bind_filter(AvailableUsers)

        self._handler = Handler(self._dp)
        self._handler.register_handlers()

        logger.info('Bot initialized!')


    async def run(self):
        logger.info('Bot is running...')
        await self._dp.skip_updates()
        await self._dp.start_polling()
