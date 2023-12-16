import unittest
from datetime import datetime
import pandas as pd
from pythonProject7.model.schedule_generator import ScheduleGenerator  # Replace 'your_module' with the name of your module



class TestScheduleGenerator(unittest.TestCase):

    def test_generate_dates(self):
        holiday_calendar = ['2023-01-01', '2023-12-25']
        holidays = pd.to_datetime(holiday_calendar)

        # Initialize ScheduleGenerator
        generator = ScheduleGenerator('1M', 'US', 'Regular', None, False)
        generator.holiday_calendar = holidays

        # Test data
        start_date = pd.to_datetime('2023-01-01')
        maturity_date = pd.to_datetime('2023-06-01')

        # Expected dates considering the holidays and weekends
        expected_dates = [
            pd.to_datetime('2023-01-02'),  # Adjusted for New Year holiday
            pd.to_datetime('2023-02-01'),
            pd.to_datetime('2023-03-01'),
            pd.to_datetime('2023-04-03'),  # Adjusted for weekend
            pd.to_datetime('2023-05-01'),
            pd.to_datetime('2023-06-01')
        ]

        # Generate dates
        generated_dates = generator.generate_dates(start_date, maturity_date)

        # Assert that the generated dates match the expected dates
        self.assertEqual(generated_dates, expected_dates)

# Run the tests
if __name__ == '__main__':
    unittest.main()
