from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from loguru import logger

from way_bill.app.states import AppState
from way_bill.app.handlers.general_data import main_menu
from way_bill.app.utils.validators import validate_float_value


async def fuel(message: types.Message, state: FSMContext):
    logger.debug(f'Add fuel request')

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('🏠 Главное Меню')

    await AppState.waiting_fuel_value.set()

    await message.answer(
        '<b>Введите количество топлива (л.)</b>\n'
        '<b>Например: 10 или 55.2</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def add_fuel_value(message: types.Message, state: FSMContext):
    fuel_value = validate_float_value(message.text.lower())
    if fuel_value is None:
        await message.answer(
            '☹️ <b>Некорректное значение топлива.</b>\n'
            '<b>Попробуйте еще раз</b>',
            parse_mode="HTML"
        )
        return await fuel(message=message, state=state)

    logger.debug(f'Got value of fuel: {fuel_value}')

    await state.update_data(fuel=fuel_value)
    await main_menu(message=message, state=state)


def register_handlers_fuel(dp: Dispatcher):
    dp.register_message_handler(
        fuel,
        text='⛽️Заправка',
        state=AppState.waiting_type_of_data
    )
    dp.register_message_handler(
        add_fuel_value,
        state=AppState.waiting_fuel_value
    )
