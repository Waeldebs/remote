import re
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import BDay
from datetime import timedelta
from pythonProject7.model.calendar_tools import Holidays_Days_countries


class ScheduleGenerator:

    def __init__(self, frequency, holiday_calendar, payment_schedule, deduction_formula, set_stub_period):
        self.frequency = frequency
        self.holiday_calendar = Holidays_Days_countries[holiday_calendar]
        self.payment_schedule = payment_schedule
        if self.payment_schedule == "Deduced from":
            self.deduction_formula = deduction_formula
        self.digit_part, self.time_value_part = self.decompose_frequency()
        self.set_stub_period = set_stub_period

    def decompose_frequency(self):
        match = re.match(r'(\d+)([A-Za-z]+)', self.frequency)
        if match:
            digit_part = int(match.group(1))
            time_value_part = match.group(2)
            return digit_part, time_value_part
        else:
            raise ValueError("Invalid frequency format")


    def adjusted_weekend(self, date):
        while date.weekday() >= 5 or date.date() in self.holiday_calendar:
            date += pd.offsets.BDay(1)
        return date


    def generate_dates(self, starting_date, maturity_date):
        dates = []
        current_date = starting_date
        while current_date <= maturity_date:
            adjusted_date = self.adjusted_weekend(current_date)
            dates.append(adjusted_date)
            if "Y" in self.time_value_part:
                current_date += relativedelta(years=self.digit_part)
            if "M" in self.time_value_part:
                current_date += relativedelta(months=self.digit_part)
            if "D" in self.time_value_part:
                current_date += relativedelta(days=self.digit_part)
        first_period = dates[:-1]
        last_period = dates[1:]
        return first_period, last_period


    def set_payment_dates(self, starting_date, maturity_date):
        end_dates = self.generate_dates(starting_date, maturity_date)[1]
        df = pd.DataFrame({"Payment Date": end_dates})
        if self.payment_schedule == "Equal to Fixing End Schedule":
            pass
        elif self.payment_schedule == "Deduced from":
            numeric_part = int(re.search(r'\d+', self.deduction_formula).group())
            if "BD" in self.deduction_formula:
                df["Payment Date"] += BDay(numeric_part)
            elif "DAYS" in self.deduction_formula:
                df["Payment Date"] += timedelta(days=numeric_part)

        return df


    def generate_equity_schedule(self, starting_date, maturity_date):
        first_period, last_period = self.generate_dates(starting_date, maturity_date)
        payment_dates = self.set_payment_dates(starting_date, maturity_date)
        df = pd.DataFrame(
            {"Fixing Start": first_period, "Fixing End": last_period, "Payment_dates": payment_dates["Payment Date"]})
        df["Fixing Start"] = pd.to_datetime(df["Fixing Start"])
        df["Fixing End"] = pd.to_datetime(df["Fixing End"])
        df["Payment_dates"] = pd.to_datetime(df["Payment_dates"])
        df["Fixing Start"] = df["Fixing Start"].dt.date
        df["Fixing End"] = df["Fixing End"].dt.date
        df["Payment_dates"] = df["Payment_dates"].dt.date

        return df

    def generate_financing_schedule(self, starting_date, maturity_date):
        first_period, last_period = self.generate_dates(starting_date, maturity_date)
        payment_dates = self.set_payment_dates(starting_date, maturity_date)
        df = pd.DataFrame(
            {"Calc Start": first_period, "Calc End": last_period, "Payment_dates": payment_dates["Payment Date"]})
        df["Calc Start"] = pd.to_datetime(df["Calc Start"])
        df["Calc End"] = pd.to_datetime(df["Calc End"])
        df["Payment_dates"] = pd.to_datetime(df["Payment_dates"])
        df["Calc Start"] = df["Calc Start"].dt.date
        df["Calc End"] = df["Calc End"].dt.date
        df["Payment_dates"] = df["Payment_dates"].dt.date

        return df
