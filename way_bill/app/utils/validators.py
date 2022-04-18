import datetime

from loguru import logger


def validate_way_bill(value: str):
    try:
        value = int(value.strip())
    except:
        logger.warning(f'Incorrect value of way bill: {value}')
        value = None
    return value


def validate_date_value(value: str):
    value = value.strip()
    if 'сегодня' in value:
        value = datetime.date.today().strftime('%d.%m.%Y')
    else:
        try:
            datetime.datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            logger.warning(f'Incorrect value of date: {value}')
            value = None
    return value


def validate_float_value(value: str):
    try:
        value = float(value.strip().replace(',', '.'))
    except:
        logger.warning(f'Incorrect value: {value}')
        value = None
    return value
