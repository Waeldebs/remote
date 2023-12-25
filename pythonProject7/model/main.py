# main.py
from pythonProject7.model.transaction import Transaction

if __name__ == "__main__":
    # Contract:
    trade_date = "02/01/2009"
    valuation_shifter = 3
    maturity = "1Y"
    stub_period_position = "inAreas"

    # Schedule

    # Performance Schedule:
    fixing_frequency = "1M"
    holiday_calendar = "USA"
    perf_payment_schedule = "Driving Schedule Deduce"
    perf_payment_frequency = "1W"
    deduction_formula_perf = None

    # Financing Schedule:
    financing_frequency = "1M"
    financing_payment_schedule = "Driving Schedule"
    financing_payment_frequency = "1M"
    deduction_formula_financing = "5BD"



    transaction_instance = Transaction(trade_date, valuation_shifter, maturity, fixing_frequency, holiday_calendar,
                                       perf_payment_schedule, perf_payment_frequency, financing_frequency,
                                       financing_payment_schedule, financing_payment_frequency,
                                       deduction_formula_perf, deduction_formula_financing, stub_period_position)

    print("Equity Schedule")
    print(transaction_instance.get_equity_schedule())

    print("")

    print("Financing Schedule")
    print(transaction_instance.get_financing_schedule())
