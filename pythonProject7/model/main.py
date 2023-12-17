# main.py
from pythonProject7.model.transaction import Transaction

if __name__ == "__main__":

    trade_date = "02/01/2009"
    valuation_shifter = 3
    maturity = "2Y"
    fixing_frequency = "2BM"
    holiday_calendar = "USA"
    perf_payment_schedule = "Deduced from"
    deduction_formula_perf = "3BD"
    financing_frequency = "1M"
    financing_payment_schedule = "Deduced from"
    deduction_formula_financing = "3BD"
    stub_period_position = "InAreas"


    transaction_instance = Transaction(trade_date, valuation_shifter, maturity, fixing_frequency, holiday_calendar,
                                       perf_payment_schedule, financing_frequency, financing_payment_schedule,
                                       deduction_formula_perf, deduction_formula_financing, stub_period_position)



    print("Financing Schedule")
    print(transaction_instance.get_financing_schedule())

    print("")

    print("Equity Schedule")
    print(transaction_instance.get_equity_schedule())

    print(transaction_instance.cc())
