code_map = {
    'AB': '01',
    'BC': '02',
    'MB': '03',
    'NB': '04',
    'NL': '05',
    'NS': '07',
    'ON': '08',
    'PE': '09',
    'QC': '10',
    'SK': '11',
    'YT': '12',
    'NT': '13',
    'NU': '14',
}


class Plugin:
    def postal_code_pre(self, parser, item):
        country_code = item['countryCode']
        if country_code != 'CA':
            return
        item['admin1Code'] = code_map[item['admin1Code']]
