from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from loguru import logger

from way_bill.app.states import AppState
from way_bill.app.handlers.general_data import main_menu
from way_bill.app.utils.validators import validate_float_value


async def add_mileage(message: types.Message, state: FSMContext):
    logger.debug(f'Add mileage request')

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Иваново', 'Москва', 'Трасса')
    keyboard.add('🏠 Главное Меню')

    await AppState.waiting_mileage_place.set()

    await message.answer(
        '<b>Выберите место поездки</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def add_mileage_place(message: types.Message, state: FSMContext):
    logger.debug(f'Selected place: {message.text.lower()}')

    await state.update_data(selected_mileage_place=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Без кондиционера', 'С кондиционером', 'Зимой')
    keyboard.add('🏠 Главное Меню')

    await AppState.waiting_mileage_type.set()

    await message.answer(
        '<b>Выберите тип поездки</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def add_mileage_type(message: types.Message, state: FSMContext):
    logger.debug(f'Selected type: {message.text.lower()}')

    await state.update_data(selected_mileage_type=message.text.lower())
    await get_mileage_value(message=message, state=state)


async def get_mileage_value(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('🏠 Главное Меню')

    await AppState.waiting_mileage_value.set()

    await message.answer(
        '<b>Введите километраж (км)</b>\n'
        '<b>Например: 10 или 55.2</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def add_mileage_value(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    mileage_data = user_data.get('mileage_data', {})
    
    milage_place = user_data['selected_mileage_place']
    milage_type = user_data['selected_mileage_type']
    
    mileage_data[milage_place] = mileage_data.get(milage_place, {})
    mileage_value = validate_float_value(message.text.lower())

    if mileage_value is None:
        await message.answer(
            '☹️ <b>Некорректное значение километража.\n</b>'
            '<b>Попробуйте еще раз</b>',
            parse_mode="HTML"
        )
        return await get_mileage_value(message=message, state=state)

    logger.debug(f'Got value of milage for {milage_place}-{milage_type}: {mileage_value}')

    mileage_data[milage_place][milage_type] = mileage_value

    await state.update_data(mileage_data=mileage_data)
    await state.update_data(selected_mileage_place=None)
    await state.update_data(selected_mileage_type=None)

    await main_menu(message=message, state=state)


def register_handlers_mileage(dp: Dispatcher):
    dp.register_message_handler(
        add_mileage,
        text='🚗Пробег',
        state=AppState.waiting_type_of_data
    )
    dp.register_message_handler(
        add_mileage_place,
        text=['Иваново', 'Москва', 'Трасса'],
        state=AppState.waiting_mileage_place
    )
    dp.register_message_handler(
        add_mileage_type,
        text=['Без кондиционера', 'С кондиционером', 'Зимой'],
        state=AppState.waiting_mileage_type
    )
    dp.register_message_handler(
        add_mileage_value,
        state=AppState.waiting_mileage_value
    )
