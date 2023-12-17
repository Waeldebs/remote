import re
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import BDay, YearEnd, BMonthEnd
from pandas.tseries.offsets import CustomBusinessDay
from datetime import timedelta
from pythonProject7.model.calendar_tools import Holidays_Days_countries
import datetime

class ScheduleGenerator:

    def __init__(self, fixing_frequency, holiday_calendar,payment_schedule, deduction_formula):

        self.frequency = fixing_frequency

        self.holiday_calendar = Holidays_Days_countries[holiday_calendar]

        self.payment_schedule = payment_schedule

        if self.payment_schedule == "Deduced from":

            self.deduction_formula = deduction_formula
        self.digit_part, self.time_value_part = self.decompose_frequency()

    def decompose_frequency(self):

        match = re.match(r'(\d+)([A-Za-z]+)', self.frequency)
        if match:
            digit_part = int(match.group(1))
            time_value_part = match.group(2)
            return digit_part, time_value_part
        else:
            raise ValueError("Invalid frequency format")

    def adjusted_weekend_holidays(self, date):
        while date.weekday() >= 5 or date in self.holiday_calendar:
            date += pd.offsets.BDay(1)
        return date


    def generate_dates(self, starting_date, maturity_date):

            dates = []
            current_date = pd.Timestamp(starting_date)
            time_value_part_upper = self.time_value_part.upper()
            while current_date <= maturity_date:
                adjusted_date = self.adjusted_weekend_holidays(current_date)
                dates.append(adjusted_date)

                if "Y" in time_value_part_upper:
                    current_date += relativedelta(years=self.digit_part)
                elif "M" in time_value_part_upper:
                    current_date += relativedelta(months=self.digit_part)
                elif "D" in time_value_part_upper:
                    current_date += relativedelta(days=self.digit_part)
                elif "BY" in time_value_part_upper:
                    current_date += YearEnd(self.digit_part)
                elif "BM" in time_value_part_upper:
                    current_date += BMonthEnd(self.digit_part)
                elif "BD" in time_value_part_upper:
                    current_date += BDay(self.digit_part)


            first_period = dates[:-1]
            last_period = dates[1:]
            return first_period, last_period, dates


    def compute_stub_period(self, starting_date, maturity_date):
            # Get the last date from the generated dates
            last_period = self.generate_dates(starting_date, maturity_date)[-1]
            last_generated_date = pd.Timestamp(last_period[-1])
            maturity_date = pd.Timestamp(maturity_date)

            # Compute the difference in calendar days
            difference_in_days = (maturity_date - last_generated_date).days

            return difference_in_days
    def generate_dates_with_stub_period(self, stub_period_position, starting_date, maturity_date):

        starting_date = pd.to_datetime(starting_date).to_pydatetime()
        maturity_date = pd.to_datetime(maturity_date).to_pydatetime()

        if stub_period_position == "upfront":
            first_period, last_period, dates = self.generate_dates(starting_date, maturity_date)
            dates.append(maturity_date)
            first_period = dates[:-1]
            last_period = dates[1:]
            return first_period, last_period

        elif stub_period_position == "InAreas":
            stub_period_last_date = starting_date + relativedelta(days=self.compute_stub_period(starting_date, maturity_date))
            first_period, last_period, _ = self.generate_dates(stub_period_last_date, maturity_date)
            first_period.insert(0, starting_date)
            last_period.insert(0, stub_period_last_date)
            return first_period, last_period

        else:
            raise ValueError(f"Invalid stub period position: {stub_period_position}")


    def set_payment_dates(self,stub_period_position, starting_date, maturity_date):
        end_dates = self.generate_dates_with_stub_period(stub_period_position, starting_date, maturity_date)[1]
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


    def generate_equity_schedule(self,stub_period_position, starting_date, maturity_date):
        first_period, last_period= self.generate_dates_with_stub_period(stub_period_position,starting_date, maturity_date)
        payment_dates = self.set_payment_dates(stub_period_position, starting_date, maturity_date)
        df = pd.DataFrame(
            {"Fixing Start": first_period, "Fixing End": last_period, "Payment_dates": payment_dates["Payment Date"]})
        df["Fixing Start"] = pd.to_datetime(df["Fixing Start"])
        df["Fixing End"] = pd.to_datetime(df["Fixing End"])
        df["Payment_dates"] = pd.to_datetime(df["Payment_dates"])
        df["Fixing Start"] = df["Fixing Start"].dt.date
        df["Fixing End"] = df["Fixing End"].dt.date
        df["Payment_dates"] = df["Payment_dates"].dt.date

        return df

    def generate_financing_schedule(self,stub_period_position, starting_date, maturity_date):
        first_period, last_period = self.generate_dates_with_stub_period(stub_period_position, starting_date, maturity_date)
        payment_dates = self.set_payment_dates(stub_period_position, starting_date, maturity_date)
        df = pd.DataFrame(
            {"Calc Start": first_period, "Calc End": last_period, "Payment_dates": payment_dates["Payment Date"]})
        df["Calc Start"] = pd.to_datetime(df["Calc Start"])
        df["Calc End"] = pd.to_datetime(df["Calc End"])
        df["Payment_dates"] = pd.to_datetime(df["Payment_dates"])
        df["Calc Start"] = df["Calc Start"].dt.date
        df["Calc End"] = df["Calc End"].dt.date
        df["Payment_dates"] = df["Payment_dates"].dt.date

        return df



schedule = ScheduleGenerator("5M", "USA", "Deduced from", "3BD")
print(schedule.compute_stub_period(starting_date=datetime.datetime(2023,1,1), maturity_date=datetime.datetime(2024,1, 1)))
