from datetime import datetime

def date_to_treat(trade_date):
    # List of expected date formats
    date_formats = ["%d-%m-%Y", "%d/%m/%Y"]

    # Check if the input is a string
    if isinstance(trade_date, str):
        for date_format in date_formats:
            try:
                # Attempt to parse the date
                new_date = datetime.strptime(trade_date, date_format)
                return new_date.date()  # Return the date part
            except ValueError:
                # If parsing fails, try the next format
                continue

        # If none of the formats worked, return an error message
        return "Invalid date format."
    else:
        # If the input is not a string, return a different error message
        return "Trade date must be a string."




Holidays_Days_countries = {
    "USA": [
        # 2023
        datetime(2023, 1, 1),
        datetime(2023, 7, 4),
        datetime(2023, 11, 11),
        datetime(2023, 12, 25),
        # 2024
        datetime(2024, 1, 1),
        datetime(2024, 7, 4),
        datetime(2024, 11, 11),
        datetime(2024, 12, 25),
    ],
    "France": [
        # 2023
        datetime(2023, 1, 1),
        datetime(2023, 5, 1),
        datetime(2023, 5, 8),
        datetime(2023, 7, 14),
        datetime(2023, 8, 15),
        # 2024
        datetime(2024, 1, 1),
        datetime(2024, 5, 1),
        datetime(2024, 5, 8),
        datetime(2024, 7, 14),
        datetime(2024, 8, 15),
        # Additional years 2025, 2026, 2027...
    ]
}


