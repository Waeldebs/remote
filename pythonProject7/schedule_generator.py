import datetime
import re
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import BDay
from datetime import timedelta

class ScheduleGenerator:

    def __init__(self, frequency, holiday_calendar, payment_schedule, deduction_formula, set_stub_period):
        self.frequency = frequency
        self.holiday_calendar = holiday_calendar
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
        while date.weekday() >= 5:
            date += pd.offsets.BDay(1)
        return date

    def generates_dates(self, starting_date, maturity_date):
            current_date = starting_date
            if isinstance(maturity_date, pd.Timestamp):
                maturity_date = maturity_date.date()
            dates = []
            # Regular schedule generation
            while True:
                next_date = self.get_next_date(current_date)
                if next_date >= maturity_date:
                    if current_date < maturity_date:
                        # Handle stub period here
                        dates.append(self.adjusted_weekend(maturity_date))
                    break
                else:
                    dates.append(self.adjusted_weekend(next_date))
                    current_date = next_date

            # Check for an upfront stub period
            if len(dates) > 0 and (dates[0] - starting_date).days > self.get_frequency_days():
                # Adjust for upfront stub
                dates.insert(1, starting_date)

            end_dates = dates[1:]
            dates = dates[:-1]
            return dates, end_dates
    def get_frequency_days(self):
        # This method returns the number of days corresponding to the frequency
        # Example: For "5M", it will return the number of days in 5 months
        if "M" in self.time_value_part:
            return 30 * self.digit_part  # Approximation
        elif "Y" in self.time_value_part:
            return 365 * self.digit_part  # Approximation
        elif "W" in self.time_value_part:
            return 7 * self.digit_part
    def get_next_date(self, current_date):
        if "W" in self.time_value_part:
            return current_date + relativedelta(weeks=self.digit_part)
        elif "M" in self.time_value_part:
            return current_date + relativedelta(months=self.digit_part)
        elif "Y" in self.time_value_part:
            return current_date + relativedelta(years=self.digit_part)

    def set_payment_dates(self, starting_date, maturity_date):
        end_dates = self.generates_dates(starting_date, maturity_date)[1]
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

    def generate_schedule(self, starting_date, maturity_date):
        dates, end_dates = self.generates_dates(starting_date, maturity_date)
        payment_dates = self.set_payment_dates(starting_date, maturity_date)
        df = pd.DataFrame({"Fixing Start": dates, "Fixing End": end_dates, "Payment_dates": payment_dates["Payment Date"]})
        df["Fixing Start"] = pd.to_datetime(df["Fixing Start"])
        df["Fixing End"] = pd.to_datetime(df["Fixing End"])
        df["Payment_dates"] = pd.to_datetime(df["Payment_dates"])
        df["Fixing Start"] = df["Fixing Start"].dt.date
        df["Fixing End"] = df["Fixing End"].dt.date
        df["Payment_dates"] = df["Payment_dates"].dt.date

        return df
