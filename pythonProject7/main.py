# main.py
from transaction import Transaction

if __name__ == "__main__":

    trade_date = "02/01/2009"
    valuation_shifter = 3
    maturity = "1Y"
    fixing_frequency = "4M"
    holiday_calendar = "USA"
    perf_payment_schedule = "Deduced from"
    deduction_formula_perf = "3BD"
    financing_frequency = "2M"
    financing_payment_schedule = "Deduced from"
    deduction_formula_financing = "3BD"
    set_stub_period = "upfront"


    transaction_instance = Transaction(trade_date, valuation_shifter, maturity, fixing_frequency, holiday_calendar,
                                       perf_payment_schedule, financing_frequency, financing_payment_schedule,
                                       deduction_formula_perf, deduction_formula_financing, set_stub_period)



    print(transaction_instance.get_schedule())
