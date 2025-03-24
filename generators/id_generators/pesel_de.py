import random

def get_days_in_month(year: int, month: int) -> int:
    """Returns the number of days in a given month of a given year."""
    if month in {1, 3, 5, 7, 8, 10, 12}:
        return 31
    elif month in {4, 6, 9, 11}:
        return 30
    elif month == 2:
        return 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
    return 0  # Should never reach this point

def generate_pkz(year: int = None, month: int = None, day: int = None, gender: str = None) -> str:
    """Generates a valid East German PKZ (Personenkennzahl)."""
    # Validate year (1900-1999)
    if year is None:
        year = random.randint(1900, 1999)
    if not 1900 <= year <= 1999:
        raise ValueError("Year must be between 1900 and 1999 (East Germany only)")

    # Validate month (1-12)
    if month is None:
        month = random.randint(1, 12)
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    # Validate day (1-28/29/30/31)
    max_day = get_days_in_month(year, month)
    if day is None:
        day = random.randint(1, max_day)
    elif not 1 <= day <= max_day:
        raise ValueError(f"Invalid day {day} for month {month} and year {year}")

    # Format date (YYMMDD)
    formatted_date = f"{year % 100:02d}{month:02d}{day:02d}"

    # Generate serial (SSS) and gender digit (G)
    serial = random.randint(0, 999)
    if gender:
        gender = gender.upper()
        gender_digit = random.choice([1, 3, 5, 7, 9]) if gender == "M" else random.choice([0, 2, 4, 6, 8]) if gender == "K" else random.randint(0, 9)
    else:
        gender_digit = random.randint(0, 9)

    # Combine into PKZ base (YYMMDDSSSG)
    pkz_base = f"{formatted_date}{serial:03d}{gender_digit}"

    # Calculate control digit (C)
    weights = [2, 1] * 5  # [2,1,2,1,2,1,2,1,2,1]
    checksum = 0
    for i in range(10):
        digit = int(pkz_base[i])
        product = digit * weights[i]
        # For products ≥ 10, sum the digits (e.g., 14 → 1 + 4 = 5)
        checksum += product if product < 10 else (product // 10) + (product % 10)
    
    control_digit = (10 - (checksum % 10)) % 10
    return f"{pkz_base}{control_digit}"