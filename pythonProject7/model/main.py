# main.py
from pythonProject7.model.transaction import Transaction
from pythonProject7.model.basket import Basket
from pythonProject7.model.components import Components

if __name__ == "__main__":

    # Contract:
    trade_date = "02/01/2009"
    valuation_shifter = 3
    maturity = "1Y"
    stub_period_position = "inAreas"

    data_components = [
        {'quantity': 100, 'price': 10.0},
        {'quantity': 200, 'price': 20.0},
        {'quantity': 200, 'price': 30.0}]

    basket = Basket(components=[])
    # Schedule

    # Performance Schedule:
    fixing_frequency = "2M"
    holiday_calendar = "USA"
    perf_payment_schedule = "Driving Schedule Deduce"
    perf_payment_frequency = "1M"
    deduction_formula_perf = None

    # Financing Schedule:
    financing_frequency = "1M"
    financing_payment_schedule = "Driving Schedule"
    financing_payment_frequency = "1M"
    deduction_formula_financing = "5BD"

    transaction_instance = Transaction(trade_date, valuation_shifter, maturity, basket, fixing_frequency,
                                       holiday_calendar,
                                       perf_payment_schedule, perf_payment_frequency, financing_frequency,
                                       financing_payment_schedule, financing_payment_frequency,
                                       deduction_formula_perf, deduction_formula_financing, stub_period_position)

    for data in data_components:
        component = Components(quantity=data['quantity'], price=data['price'])
        basket.add_component(component)

    print("Equity Schedule")
    print(transaction_instance.get_equity_schedule())

    print("")

    print("Financing Schedule")
    print(transaction_instance.get_financing_schedule())

    print(transaction_instance.perf_leg.basket.gg())
