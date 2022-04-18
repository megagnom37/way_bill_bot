
class WayBillBody:
    def __init__(self, data: dict, sheet_name: str, row_id: int):
        self._data = data
        self._sheet_name = sheet_name
        self._row_id = row_id
        self._body_dict = {}
        self._build()
    
    def _build(self):
        common_fields = self._get_common_fields()
        mileage_fields = self._get_mileage_fields()
        self._body_dict = {
            'valueInputOption' : 'RAW',
            'data' : [*common_fields, *mileage_fields]
        }

    def _get_common_fields(self):
        res = []

        fields = {
            'way_bill_number': 'B',
            'date': 'C',
            'downtime': 'Q',
            'fuel': 'U'
        }

        for field in fields:
            if field in self._data:
                field_dict = {
                    'range': f'{self._sheet_name}!{fields[field]}{self._row_id}', 
                    'values': [[self._data[field]]]
                }
                res.append(field_dict)

        return res

    def _get_mileage_fields(self):
        res = []

        if 'mileage_data' not in self._data:
            return res

        mileage_data = self._data['mileage_data']

        places = [
            'иваново',
            'москва',
            'трасса'
        ]
        way_types = {
            'без кондиционера': ('E', 'I', 'M'),
            'с кондиционером': ('F', 'J', 'N'),
            'зимой': ('G', 'K', 'O'),
        }

        for i, place in enumerate(places):
            if place in mileage_data:
                place_data = mileage_data[place]
                for way_type in way_types:
                    if way_type in place_data:
                        cell_range = f'{self._sheet_name}!{way_types[way_type][i]}{self._row_id}'
                        values = [[place_data[way_type]]]
                        field_dict = {'range': cell_range, 'values': values}
                        res.append(field_dict)

        return res

    @property
    def as_dict(self):
        return self._body_dict
