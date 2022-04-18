from aiogram import Dispatcher

from way_bill.app.handlers.common import register_handlers_common
from way_bill.app.handlers.general_data import register_handlers_general_data
from way_bill.app.handlers.mileage import register_handlers_mileage
from way_bill.app.handlers.downtime import register_handlers_downtime
from way_bill.app.handlers.fuel import register_handlers_fuel


class Handler:
    HANDLERS = [
        register_handlers_common,
        register_handlers_general_data,
        register_handlers_mileage,
        register_handlers_downtime,
        register_handlers_fuel
    ]

    def __init__(self, dp: Dispatcher):
        self._dp = dp

    def register_handlers(self):
        for handler in self.HANDLERS:
            handler(self._dp)
