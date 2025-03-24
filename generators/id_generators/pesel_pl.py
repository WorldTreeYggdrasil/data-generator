import random

def generate_id_number(year: int = None, month: int = None, day: int = None, gender: str = None):
    """Alias for generate_pesel to maintain compatibility with the generator."""
    return generate_pesel(year, month, day, gender)

def is_leap_year(year: int) -> bool:
    """Determine if a year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def get_days_in_month(year: int, month: int) -> int:
    """Returns the number of days in a given month of a given year."""
    if month in {1, 3, 5, 7, 8, 10, 12}:
        return 31
    elif month in {4, 6, 9, 11}:
        return 30
    elif month == 2:
        return 29 if is_leap_year(year) else 28
    return 0  # Should never reach this point with proper validation

def generate_pesel(year: int = None, month: int = None, day: int = None, gender: str = None):
    """
    Generates a valid PESEL number along with the corresponding birth date.
    
    Args:
        year: Birth year (1800-2299)
        month: Birth month (1-12)
        day: Birth day (1-31, depending on month)
        gender: 'M' for male, 'K' for female, None for random
    
    Returns:
        Tuple of (PESEL_number, birth_date_as_YYYY-MM-DD)
    """
    # Validate or generate year
    if year is None:
        year = random.randint(1800, 2299)
    elif not 1800 <= year <= 2299:
        raise ValueError("Year must be between 1800 and 2299")

    # Determine month offset based on century
    if 1800 <= year <= 1899:
        month_offset = 80
    elif 1900 <= year <= 1999:
        month_offset = 0
    elif 2000 <= year <= 2099:
        month_offset = 20
    elif 2100 <= year <= 2199:
        month_offset = 40
    elif 2200 <= year <= 2299:
        month_offset = 60
    else:
        raise ValueError("Year out of valid range")

    # Validate or generate month
    if month is None:
        month = random.randint(1, 12)
    elif not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    # Validate or generate day
    max_day = get_days_in_month(year, month)
    if day is None:
        day = random.randint(1, max_day)
    elif not 1 <= day <= max_day:
        raise ValueError(f"Invalid day {day} for month {month} and year {year}")

    # Format birth date
    birth_date = f"{year}-{month:02d}-{day:02d}"

    # PESEL components
    yy = f"{year % 100:02d}"
    mm = f"{month + month_offset:02d}"
    dd = f"{day:02d}"

    # Generate serial number and gender digit
    sss = random.randint(0, 999)
    if gender and gender.upper() == 'M':
        gender_digit = random.choice([1, 3, 5, 7, 9])
    elif gender and gender.upper() == 'K':
        gender_digit = random.choice([0, 2, 4, 6, 8])
    else:
        gender_digit = random.randint(0, 9)
    
    serial = f"{sss:03d}{gender_digit}"

    # Construct base PESEL (10 digits)
    pesel_base = f"{yy}{mm}{dd}{serial}"

    # Calculate control digit
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = sum(int(pesel_base[i]) * weights[i] for i in range(10)) % 10
    control_digit = (10 - checksum) % 10

    pesel = pesel_base + str(control_digit)

    return pesel, birth_date