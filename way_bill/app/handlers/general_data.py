from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hlink
from loguru import logger

from way_bill.app.states import AppState
from way_bill.app.utils.validators import validate_way_bill, validate_date_value
from way_bill.app.handlers.common import add_record, cmd_start
from way_bill.app.google.core import google_worker

from way_bill.app.config import config


async def add_way_bill(message: types.Message, state: FSMContext):
    way_bill_value = validate_way_bill(message.text.lower())

    if way_bill_value is None:
        await message.answer(
            '☹️ <b>Некорректное значение путевого листа.</b>\n'
            '<b>Попробуйте еще раз</b>',
             parse_mode="HTML"
        )
        return await add_record(message=message, state=state)

    logger.debug(f'Got value of way bill number: {way_bill_value}')

    await state.update_data(way_bill_number=way_bill_value)
    await date(message=message, state=state)


async def date(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('📆 Сегодня')
    keyboard.add('❌ Отмена')

    await AppState.waiting_date.set()

    await message.answer(
        '<b>Введитее дату или нажмите кнопку "Сегодня"</b>\n'
        '<b>(формат: "ДД.ММ.ГГГГ")</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def add_date(message: types.Message, state: FSMContext):
    date_value = validate_date_value(message.text.lower())
    if date_value is None:
        await message.answer(
            '☹️ <b>Некорректное значение даты.</b>\n'
            '<b>Попробуйте еще раз</b>',
            parse_mode="HTML"
        )
        return await date(message=message, state=state)

    logger.debug(f'Got value of date: {date_value}')

    await state.update_data(date=date_value)
    await main_menu(message=message, state=state)


async def main_menu(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('🚗Пробег', '🕒Простой', '⛽️Заправка')
    keyboard.add('💾Сохранить', '❌Отмена')

    await AppState.waiting_type_of_data.set()

    await message.answer(
        '<b>Выберите, что хотите добавить.</b>\n'
        '<b>В конце не забудьте "Сохранить" результаты!</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def save(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    logger.debug(f'Save request: {user_data}')

    try:
        is_saved = google_worker.try_to_save(user_data)
    except Exception:
        await message.answer(
            '<b>Что-то пошло не так!</b>\n'
            '<b>Напишите Ивану и он все исправит</b>\n'
            '<b>Но это не точно</b>',
            parse_mode="HTML"
        )
        return await cmd_start(message=message, state=state)
    if is_saved:
        logger.debug('Successfully saved')
        await message.answer(
            '✅ <b>Успепшно сохранено</b>',
            parse_mode="HTML"
        )
        await cmd_start(message=message, state=state)
    else:
        logger.debug(f'Record with date {user_data["date"]} already exists')

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('📝 Заменить')
        keyboard.add('❌ Отмена')

        await AppState.waiting_replace_handling.set()

        link = f'https://docs.google.com/spreadsheets/d/{config["way_bill_google_spreadsheet"]}'
        link = hlink('Таблица', link)

        await message.answer(
            f'<b>Запись с датой: {user_data["date"]} уже существует!</b>\n'
            '<b>Проверьте таблицу и выберите, что хотите сделать</b>\n\n'
            f'<b>{link}</b>',
            parse_mode="HTML",
            reply_markup=keyboard
        )


async def replace(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    logger.debug(f'Replace request: {user_data}')

    google_worker.replace(user_data)

    await message.answer(
        '✅ <b>Успепшно сохранено</b>',
        parse_mode="HTML"
    )
    await cmd_start(message=message, state=state)


def register_handlers_general_data(dp: Dispatcher):
    dp.register_message_handler(
        add_way_bill, 
        state=AppState.waiting_way_bill
    )
    dp.register_message_handler(
        add_date, 
        state=AppState.waiting_date
    )
    dp.register_message_handler(
        main_menu, 
        text='🏠 Главное Меню', 
        state=[
            AppState.waiting_mileage_place, 
            AppState.waiting_mileage_type,
            AppState.waiting_mileage_value,
            AppState.waiting_downtime_value,
            AppState.waiting_fuel_value,
        ]
    )
    dp.register_message_handler(
        save,
        text='💾Сохранить',
        state=AppState.waiting_type_of_data
    )
    dp.register_message_handler(
        replace,
        text='📝 Заменить',
        state=AppState.waiting_replace_handling
    )


