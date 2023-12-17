# main.py
from pythonProject7.model.transaction import Transaction

if __name__ == "__main__":

    trade_date = "02/01/2009"
    valuation_shifter = 3
    maturity = "1Y"
    fixing_frequency = "5M"
    holiday_calendar = "USA"
    perf_payment_schedule = "Deduced from"
    deduction_formula_perf = "3BD"
    financing_frequency = "5M"
    financing_payment_schedule = "Deduced from"
    deduction_formula_financing = "5BD"
    stub_period_position = "upfront"


    transaction_instance = Transaction(trade_date, valuation_shifter, maturity, fixing_frequency, holiday_calendar,
                                       perf_payment_schedule, financing_frequency, financing_payment_schedule,
                                       deduction_formula_perf, deduction_formula_financing, stub_period_position)



    print("Financing Schedule")
    print(transaction_instance.get_financing_schedule())

    print("")

    print("Equity Schedule")
    print(transaction_instance.get_equity_schedule())

