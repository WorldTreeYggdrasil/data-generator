import random

def generate_id_number(year: int = None, month: int = None, day: int = None, gender: str = None):
    """
    Generates a German-style ID number along with birth date.
    
    Args:
        year: Birth year (1900-2099)
        month: Birth month (1-12)
        day: Birth day (1-31, depending on month)
        gender: Not used in German IDs (maintained for compatibility)
    
    Returns:
        Tuple of (ID_number, birth_date_as_YYYY-MM-DD)
    """
    # Validate or generate year
    if year is None:
        year = random.randint(1900, 2099)
    elif not 1900 <= year <= 2099:
        raise ValueError("Year must be between 1900 and 2099")

    # Validate or generate month
    if month is None:
        month = random.randint(1, 12)
    elif not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    # Validate or generate day
    max_day = 31 if month in {1, 3, 5, 7, 8, 10, 12} else \
              30 if month in {4, 6, 9, 11} else \
              28 if year % 4 != 0 or (year % 100 == 0 and year % 400 != 0) else 29
    if day is None:
        day = random.randint(1, max_day)
    elif not 1 <= day <= max_day:
        raise ValueError(f"Invalid day {day} for month {month} and year {year}")

    # Format birth date
    birth_date = f"{year}-{month:02d}-{day:02d}"

    # Generate random 9-digit number
    random_part = random.randint(0, 999999999)
    
    # Construct base ID (10 digits: YYMMDD + random 4 digits)
    id_base = f"{year % 100:02d}{month:02d}{day:02d}{random_part:04d}"

    # Calculate simple checksum (sum of digits mod 10)
    checksum = sum(int(d) for d in id_base) % 10
    id_number = id_base + str(checksum)

    return id_number, birth_date
