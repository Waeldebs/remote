import re
import pandas as pd
from pandas.tseries.offsets import BDay
from pythonProject7.model.calendar_tools import date_to_treat
from dateutil.relativedelta import relativedelta

from pythonProject7.model.schedule_generator import ScheduleGenerator
from pythonProject7.model.perf_leg import PerfLeg
from pythonProject7.model.financing_leg import FinancingLeg

class Transaction:

    def __init__(self, trade_date, valuation_shifter: int, maturity, fixing_frequency, holiday_calendar, perf_payment_schedule,
                 financing_frequency, financing_payment_schedule, deduction_formula_perf, deduction_formula_financing, stub_period_position):

        self.trade_date = date_to_treat(trade_date)
        self.valuation_shifter = valuation_shifter
        self.maturity = maturity
        self.stub_period_position = stub_period_position

        perf_schedule_generator = ScheduleGenerator(fixing_frequency, holiday_calendar, perf_payment_schedule, deduction_formula_perf)
        self.perf_leg = PerfLeg(perf_schedule_generator)

        financing_schedule_generator = ScheduleGenerator(financing_frequency, holiday_calendar, financing_payment_schedule, deduction_formula_financing)
        self.financing_leg = FinancingLeg(financing_schedule_generator)

    def decompose_string(self, s):
        match = re.match(r"(\d+)([A-Za-z]+)", s)
        if match:
            numeric_part = match.group(1)
            alphabetic_part = match.group(2)
            return numeric_part, alphabetic_part
        else:
            return "Invalid format", None

    @property
    def effective_date(self):
        effective_date = self.trade_date + BDay(self.valuation_shifter)
        return effective_date

    @staticmethod
    def adjusted_weekend(date):
        while date.weekday() >= 5:
            date += pd.offsets.BDay(1)
        return date

    @property
    def maturity_date(self):
        numeric_part, alphabetic_part = self.decompose_string(self.maturity)
        if alphabetic_part is None:
            return "Invalid maturity format"

        start_date = self.effective_date
        numeric_part = int(numeric_part)  # Convert to integer

        if "Y" in alphabetic_part:
            maturity_date = start_date + relativedelta(years=numeric_part)
        elif "M" in alphabetic_part:
            maturity_date = start_date + relativedelta(months=numeric_part)
        elif "W" in alphabetic_part:
            maturity_date = start_date + relativedelta(weeks=numeric_part)
        else:
            return "Invalid maturity format"

        return pd.to_datetime(self.adjusted_weekend(maturity_date))


    def get_equity_schedule(self):
        return self.perf_leg.schedule_generator.generate_equity_schedule(starting_date= pd.to_datetime(self.trade_date), maturity_date = self.maturity_date, stub_period_position=self.stub_period_position)

    def get_financing_schedule(self):
        return self.perf_leg.schedule_generator.generate_financing_schedule(starting_date= pd.to_datetime(self.effective_date), maturity_date = self.maturity_date, stub_period_position=self.stub_period_position)


    def cc(self):
        return self.perf_leg.schedule_generator.compute_stub_period(starting_date=self.trade_date, maturity_date=self.maturity_date)
