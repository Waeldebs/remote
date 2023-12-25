import unittest
from your_module_name import ScheduleGenerator  # Replace with the actual name of your module

class TestDecomposeFrequency(unittest.TestCase):

    def setUp(self):
        # Initialize ScheduleGenerator with dummy values as they are not used in decompose_frequency
        self.generator = ScheduleGenerator("DummyFrequency", "DummyCalendar", "DummySchedule")

    def test_valid_frequencies(self):
        valid_frequencies = {
            "1M": (1, "M"),
            "3Y": (3, "Y"),
            "12D": (12, "D"),
            # Add more valid test cases as needed
        }

        for freq, expected in valid_frequencies.items():
            with self.subTest(frequency=freq):
                result = self.generator.decompose_frequency(freq)
                self.assertEqual(result, expected)

    def test_invalid_frequencies(self):
        invalid_frequencies = ["M1", "YY", "abc", ""]

        for freq in invalid_frequencies:
            with self.subTest(frequency=freq):
                with self.assertRaises(ValueError):
                    self.generator.decompose_frequency(freq)

if __name__ == '__main__':
    unittest.main()
