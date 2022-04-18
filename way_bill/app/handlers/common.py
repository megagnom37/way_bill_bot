from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hlink

from way_bill.app.states import AppState
from way_bill.app.utils.filters import AvailableUsers
from way_bill.app.config import config


async def cmd_start(message: types.Message, state: FSMContext):
    logger.debug('Bot start command requested')

    await state.finish()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('✏️ Добавить запись')
    keyboard.add('📊 Посмотреть таблицу')

    await AppState.waiting_type_of_action.set()
    await message.answer(
        '<b>Выберите, что хотите сделать</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def add_record(message: types.Message, state: FSMContext):
    logger.debug('Add record requested')

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('❌ Отмена')

    await AppState.waiting_way_bill.set()

    await message.answer(
        '<b>Введитее номер путевого листа</b>\n'
        '<b>Например: 12345</b>',
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def show_table(message: types.Message, state: FSMContext):
    logger.debug('Show table requested')

    link = f'https://docs.google.com/spreadsheets/d/{config["way_bill_google_spreadsheet"]}'
    link = hlink('Таблица', link)

    await message.answer(
        f'<b>{link}</b>',
        parse_mode="HTML",
    )
    await cmd_start(message=message, state=state)


async def cancel(message: types.Message, state: FSMContext):
    logger.debug('Cancel request')

    await message.answer(
        '❌ <b>Добавление записи отменено</b>',
        parse_mode="HTML"
    )

    await cmd_start(message=message, state=state)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(
        cmd_start, 
        AvailableUsers(),
        commands="start", 
        state="*",
    )
    dp.register_message_handler(
        cancel, 
        text='❌ Отмена', 
        state=[
            AppState.waiting_way_bill, 
            AppState.waiting_date,
            AppState.waiting_type_of_data,
            AppState.waiting_replace_handling
        ]
    )
    dp.register_message_handler(
        add_record, 
        text='✏️ Добавить запись', 
        state=AppState.waiting_type_of_action
    )
    dp.register_message_handler(
        show_table, 
        text='📊 Посмотреть таблицу', 
        state=AppState.waiting_type_of_action
    )
