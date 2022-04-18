from aiogram.dispatcher.filters.state import State, StatesGroup


class AppState(StatesGroup):
    waiting_type_of_action = State()
    waiting_way_bill = State()
    waiting_date = State()
    waiting_type_of_data = State()
    waiting_mileage_place = State()
    waiting_mileage_type = State()
    waiting_mileage_value = State()
    waiting_downtime_value = State()
    waiting_fuel_value = State()
    waiting_replace_handling = State()
