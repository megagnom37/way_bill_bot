from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from loguru import logger

from way_bill.app.states import AppState
from way_bill.app.handlers.general_data import main_menu
from way_bill.app.utils.validators import validate_float_value


async def downtime(message: types.Message, state: FSMContext):
    logger.debug(f'Add downtime request')

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('🏠 Главное Меню')

    await AppState.waiting_downtime_value.set()

    await message.answer(
        '<b>Введите время простоя (ч.)</b>\n'
        '<b>Например: 2</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def add_downtime_value(message: types.Message, state: FSMContext):
    downtime_value = validate_float_value(message.text.lower())
    if downtime_value is None:
        await message.answer(
            '☹️ <b>Некорректное значение простоя.</b>\n'
            '<b>Попробуйте еще раз</b>',
            parse_mode="HTML"
        )
        return await downtime(message=message, state=state)

    logger.debug(f'Got value of downtime: {downtime_value}')

    await state.update_data(downtime=downtime_value)
    await main_menu(message=message, state=state)


def register_handlers_downtime(dp: Dispatcher):
    dp.register_message_handler(
        downtime,
        text='🕒Простой',
        state=AppState.waiting_type_of_data
    )
    dp.register_message_handler(
        add_downtime_value,
        state=AppState.waiting_downtime_value
    )
