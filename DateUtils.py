
def date_to_str_ddMMyyyy(date):
    day, month, year = str(date.day).zfill(2), str(date.month).zfill(2), str(date.year).zfill(4)
    return f'{day}/{month}/{year}'
