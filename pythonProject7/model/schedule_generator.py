import re
import pandas_market_calendars as mcal
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import BDay, YearEnd, BMonthEnd
from datetime import timedelta
from pythonProject7.model.calendar_tools import Holidays_Days_countries
import datetime


class ScheduleGenerator:
    def __init__(self, fixing_frequency, holiday_calendar, payment_schedule, payment_frequency=None,
                 deduction_formula=None):

        self.fixing_frequency = fixing_frequency
        self.fixing_digit_part, self.fixing_time_value_part = self.decompose_frequency(self.fixing_frequency)
        self.holiday_calendar = Holidays_Days_countries[holiday_calendar]
        self.payment_schedule = payment_schedule

        if self.payment_schedule == "Driving Schedule":
            self.payment_frequency = payment_frequency
            self.payment_digit_part, self.payment_time_value_part = self.decompose_frequency(self.payment_frequency)

        elif self.payment_schedule == "Driving Schedule Deduce":
            self.payment_frequency = payment_frequency
            self.payment_digit_part, self.payment_time_value_part = self.decompose_frequency(self.payment_frequency)

        elif self.payment_schedule == "Deduced from":
            self.deduction_formula = deduction_formula

            self.payment_digit_part, self.payment_time_value_part = None, None

            self.fixing_digit_part, self.fixing_time_value_part = self.decompose_frequency(self.fixing_frequency)

    def decompose_frequency(self, frequency):
        match = re.match(r'(\d+)([A-Za-z]+)', frequency)
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

    def get_holiday_calendar(self):
        return self.holiday_calendar

    def get_calendar_exchange_schedule(self, starting_date, maturity,
                                       exchange_market=None):  # only USA so exchange set to "NYSE"
        if self.holiday_calendar == "USA":
            exchange_market = "NYSE"
            nyse_calendar = mcal.get_calendar(exchange_market)
            full_schedule = nyse_calendar.schedule(start_date=starting_date, end_date=maturity)
            return full_schedule

    def generate_dates(self, starting_date, maturity_date):

        full_schedule = self.get_calendar_exchange_schedule(starting_date,
                                                            maturity_date)  # To compute open days if frequency is set to open
        dates = []
        current_date = pd.Timestamp(self.adjusted_weekend_holidays(starting_date))
        time_value_part_upper = self.fixing_time_value_part.upper()
        while current_date <= maturity_date:
            adjusted_date = self.adjusted_weekend_holidays(current_date)
            dates.append(adjusted_date)

            if "Y" in time_value_part_upper:
                current_date += relativedelta(years=self.fixing_digit_part)
            elif "M" in time_value_part_upper:
                current_date += relativedelta(months=self.fixing_digit_part)
            elif "D" in time_value_part_upper:
                current_date += relativedelta(days=self.fixing_digit_part)
            elif "BY" in time_value_part_upper:
                current_date += YearEnd(self.fixing_digit_part)
            elif "BM" in time_value_part_upper:
                current_date += BMonthEnd(self.fixing_digit_part)
            elif "BD" in time_value_part_upper:
                current_date += BDay(self.fixing_digit_part)
            elif "W" in time_value_part_upper:
                current_date += relativedelta(weeks=self.fixing_digit_part)
            elif "BW" in time_value_part_upper:
                current_date += pd.offsets.BDay(5 * self.fixing_digit_part)
            elif "OD" in time_value_part_upper:
                current_date += full_schedule.iloc[self.fixing_digit_part - 1: self.fixing_digit_part]
            elif "OW" in time_value_part_upper:
                current_date += full_schedule.iloc[self.fixing_digit_part - 1: self.fixing_digit_part * 5]

        first_period = dates[:-1]
        last_period = dates[1:]
        return first_period, last_period, dates

    def compute_stub_period(self, starting_date, maturity_date):
        last_period = self.generate_dates(starting_date, maturity_date)[-1]
        last_generated_date = pd.Timestamp(last_period[-1])
        maturity_date = pd.Timestamp(maturity_date)
        difference_in_days = (maturity_date - last_generated_date).days - 3
        return difference_in_days

    def generate_dates_with_stub_period(self, stub_period_position, starting_date, maturity_date):

        if stub_period_position == "inAreas":
            first_period, last_period, dates = self.generate_dates(starting_date, maturity_date)
            if maturity_date != last_period[-1]:
                dates.append(maturity_date)
            first_period = dates[:-1]
            last_period = dates[1:]
            return first_period, last_period

        elif stub_period_position == "upfront":
            stub_period_position_first_date = starting_date
            stub_period_last_date = stub_period_position_first_date + relativedelta(
                  days=self.compute_stub_period(starting_date, maturity_date))
            _, _, dates = self.generate_dates(stub_period_last_date, maturity_date)
            dates.insert(0, starting_date)
            first_period = dates[:-1]
            last_period = dates[1:]
            return first_period, last_period
        else:
            raise ValueError(f"Invalid stub period position: {stub_period_position}")

        # TODO: Add non existent stub_period to the model

    def set_payment_dates(self, stub_period_position, starting_date, maturity_date, valuation_shifter):

        end_dates = self.generate_dates_with_stub_period(stub_period_position, starting_date, maturity_date)[1]
        df = pd.DataFrame(data=None, columns=["Payment Date"])

        if self.payment_schedule == "Equal to Fixing End Schedule":
           df = pd.DataFrame({"Payment Date": end_dates})

        elif self.payment_schedule == "Deduced from":
             df = pd.DataFrame({"Payment Date": end_dates})
             numeric_part = int(re.search(r'\d+', self.deduction_formula).group())
             if "BD" in self.deduction_formula:
                 df["Payment Date"] += BDay(numeric_part)
             elif "DAYS" in self.deduction_formula:
                 df["Payment Date"] += timedelta(days=numeric_part)
                 df["Payment Date"] = df["Payment Date"].apply(lambda x: self.adjusted_weekend_holidays(x))

        elif self.payment_schedule == "Driving Schedule":
            df = pd.DataFrame(data=end_dates, columns=["End Dates"])
            if "MONTH" in self.payment_time_value_part or "M" in self.payment_time_value_part:
                df["Payment Date"] = (df["End Dates"].apply(lambda x: x + relativedelta(months=self.payment_digit_part))).apply(lambda x: self.adjusted_weekend_holidays(x))
            elif "WEEKS" in self.payment_time_value_part or "W" in self.payment_time_value_part:
                df["Payment Date"] = (df["End Dates"].apply(lambda x: x + relativedelta(weeks=self.payment_digit_part))).apply(lambda x: self.adjusted_weekend_holidays(x))
            elif "YEARS" in self.payment_time_value_part or "Y" in self.payment_time_value_part:
                df["Payment Date"] = (df["End Dates"].apply(lambda x: x + relativedelta(years=self.payment_digit_part))).apply(lambda x: self.adjusted_weekend_holidays(x))
            elif "DAYS" in self.payment_time_value_part or "D" in self.payment_time_value_part:
                df["Payment Date"] = (df["End Dates"].apply(lambda x: x + relativedelta(days=self.payment_digit_part))).apply(lambda x: self.adjusted_weekend_holidays(x))
            elif "BUSINESSDAYS" in self.payment_time_value_part or "BD" in self.payment_time_value_part:
                df["Payment Date"] = df["End Dates"].apply(lambda x: x + BDay(self.payment_digit_part))

        elif self.payment_schedule == "Driving Schedule Deduce":
            df = pd.DataFrame(data=end_dates, columns=["End Dates"])
            if "MONTH" or "M" in self.payment_time_value_part:
                df["Payment Date"] = df["End Dates"].apply(lambda x: x + relativedelta(months=self.payment_digit_part))
                df["Payment Date"] += BDay(valuation_shifter)
            elif "WEEKS" or "W" in self.payment_time_value_part:
                df["Payment Date"] = df["End Dates"].apply(lambda x: x + relativedelta(weeks=self.payment_digit_part))
                df["Payment Date"] += BDay(valuation_shifter)
            elif "YEARS" or "Y" in self.payment_time_value_part:
                df["Payment Date"] = df["End Dates"].apply(lambda x: x + relativedelta(years=self.payment_digit_part))
                df["Payment Date"] += BDay(valuation_shifter)
            elif "DAYS" or "D" in self.payment_time_value_part:
                df["Payment Date"] = df["End Dates"].apply(lambda x: x + relativedelta(days=self.payment_digit_part))
                df["Payment Date"] += BDay(valuation_shifter)
            elif "BUSINESSDAYS" or "BD" in self.payment_time_value_part:
                df["Payment Date"] = df["End Dates"].apply(lambda x: x + BDay(self.payment_digit_part))
                df["Payment Date"] += BDay(valuation_shifter)
            else:

                ValueError(f"Payment Schedule not Valid")

        return df

    def generate_equity_schedule(self, stub_period_position, starting_date, maturity_date, valuation_shifter):

        first_period, last_period = self.generate_dates_with_stub_period(stub_period_position, starting_date, maturity_date)
        payment_dates = self.set_payment_dates(stub_period_position, starting_date, maturity_date, valuation_shifter)
        df = pd.DataFrame({"Fixing Start": first_period, "Fixing End": last_period, "Payment_dates": payment_dates["Payment Date"]})
        df["Fixing Start"] = pd.to_datetime(df["Fixing Start"])
        df["Fixing End"] = pd.to_datetime(df["Fixing End"])
        df["Payment_dates"] = pd.to_datetime(df["Payment_dates"])
        df = df[df['Fixing Start'] != df['Fixing End']]
        df["Fixing Start"] = df["Fixing Start"].dt.date
        df["Fixing End"] = df["Fixing End"].dt.date
        df["Payment_dates"] = df["Payment_dates"].dt.date

        return df

    def generate_financing_schedule(self, stub_period_position, starting_date, maturity_date, valuation_shifter):

        first_period, last_period = self.generate_dates_with_stub_period(stub_period_position, starting_date, maturity_date)
        payment_dates = self.set_payment_dates(stub_period_position, starting_date, maturity_date, valuation_shifter)
        df = pd.DataFrame({"Calc Start": first_period, "Calc End": last_period, "Payment_dates": payment_dates["Payment Date"]})
        df["Calc Start"] = pd.to_datetime(df["Calc Start"])
        df["Calc End"] = pd.to_datetime(df["Calc End"])
        df["Payment_dates"] = pd.to_datetime(df["Payment_dates"])
        df = df[df['Calc Start'] != df['Calc End']]
        df["Calc Start"] = df["Calc Start"].dt.date
        df["Calc End"] = df["Calc End"].dt.date
        df["Payment_dates"] = df["Payment_dates"].dt.date

        return df


# Example usage
schedule = ScheduleGenerator("1M", "USA", "Driving Schedule", "1W")
print(schedule.set_payment_dates(stub_period_position="upfront", starting_date=datetime.datetime(2023, 2, 1), maturity_date=datetime.datetime(2024, 1, 1), valuation_shifter=3))
