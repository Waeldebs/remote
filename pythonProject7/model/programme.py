import datetime
import pandas as pd


def adjusted_weekend_holidays(date):
    while date.weekday() >= 5:
        date += pd.offsets.BDay(1)
    return date


print(adjusted_weekend_holidays(date=datetime.datetime(2009, 3, 7)))
