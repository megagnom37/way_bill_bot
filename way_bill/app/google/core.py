from collections import namedtuple

import httplib2
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from way_bill.app.utils.dates import get_month_name
from way_bill.app.google.body import WayBillBody
from way_bill.app.config import config


RecordInfo = namedtuple('RecordInfo', ('exists', 'index'))


class GoogleWorker:
    START_ROW_ID = 6

    def __init__(self):
        self.creds_json_path = config['way_bill_google_creds_path']
        self.scopes = [config['way_bill_google_scope']]
        self.sheet_id = config['way_bill_google_spreadsheet']
        self._last_record_info = None

        self.service = self._build_service()

    def _build_service(self):
        creds_service = ServiceAccountCredentials.from_json_keyfile_name(
            self.creds_json_path, 
            self.scopes
        )
        creds_service = creds_service.authorize(httplib2.Http())

        return build('sheets', 'v4', http=creds_service)

    def try_to_save(self, user_data: dict) -> bool:
        record_date = user_data['date']
        month_name = get_month_name(record_date)
        record_info = self._get_insert_row_id(record_date, month_name)

        if not record_info.exists:
            self._write_data(user_data, month_name, record_info.index)
            return True

        self._last_record_info = record_info

        return False

    def replace(self, user_data: dict):
        month_name = get_month_name(user_data['date'])
        self._clear_old_record(month_name, self._last_record_info.index)
        self._write_data(user_data, month_name, self._last_record_info.index)

    def _get_insert_row_id(self, date: str, sheet_name: str) -> RecordInfo:
        resp = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, 
            range=f'{sheet_name}!C6:C28'
        ).execute()

        dates = resp.get('values')
        if dates:
            dates = [i for sublist in dates for i in sublist]
        else:
            dates = []

        try:
            row_index = dates.index(date)
        except ValueError:
            return RecordInfo(False, self.START_ROW_ID + len(dates))
        else:
            return RecordInfo(True, self.START_ROW_ID + row_index)

    def _write_data(self, user_data: dict, sheet_name: str, row_index: int):
        body = WayBillBody(user_data, sheet_name, row_index)
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.sheet_id, 
            body=body.as_dict
        ).execute()

    def _clear_old_record(self, sheet_name: str, row_index: int):
        clear_data = {
            'way_bill_number': '', 
            'date': '', 
            'mileage_data': {
                'иваново': {
                    'без кондиционера': '', 
                    'с кондиционером': '', 
                    'зимой': ''
                }, 
                'москва': {
                    'без кондиционера': '', 
                    'с кондиционером': '',
                    'зимой': ''
                }, 
                'трасса': {
                    'без кондиционера': '', 
                    'с кондиционером': '', 
                    'зимой': ''
                }
            }, 
            'downtime': '', 
            'fuel': ''
        }

        self._write_data(clear_data, sheet_name, row_index)


google_worker = GoogleWorker()
