from aiogram.dispatcher.filters import Filter
from aiogram import types

from way_bill.app.config import config


class AvailableUsers(Filter):
    key = "available_users"

    AVAILABLE_USERS = set(
        map(int, config['way_bill_telegram_users'].split(';'))
    )

    async def check(self, message: types.Message):
        return message.from_user.id in self.AVAILABLE_USERS
