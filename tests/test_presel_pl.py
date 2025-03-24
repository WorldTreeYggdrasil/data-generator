import pytest
from generators.id_generators.pesel_pl import generate_pesel
from generators.base_generator import PersonalDataGeneratorBase

def test_generate_pesel():
    pesel, birth_date = generate_pesel(2000, 5, 15, "M")
    assert len(pesel) == 11, "PESEL should be 11 characters long"
    assert pesel.isdigit(), "PESEL should contain only digits"
    assert birth_date == "2000-05-15", "Birth date should match input parameters"

def test_generate_pesel_gender():
    pesel_male, _ = generate_pesel(1990, 10, 20, "M")
    pesel_female, _ = generate_pesel(1990, 10, 20, "K")

    assert int(pesel_male[-2]) % 2 == 1, "Males should have an odd 10th digit"
    assert int(pesel_female[-2]) % 2 == 0, "Females should have an even 10th digit"

def test_generate_pesel_invalid_year():
    with pytest.raises(ValueError, match="Year must be between 1800 and 2299"):
        generate_pesel(1700, 5, 15)

def test_generate_pesel_invalid_month():
    with pytest.raises(ValueError, match="Month must be between 1 and 12"):
        generate_pesel(2000, 13, 10)

def test_generate_pesel_invalid_day():
    with pytest.raises(ValueError, match=r"Invalid day 32 for month 1 and year 2000"):
        generate_pesel(2000, 1, 32)

def test_generate_pesel_leap_year():
    pesel_leap, birth_date = generate_pesel(2000, 2, 29, "M")
    assert len(pesel_leap) == 11, "PESEL should be 11 characters long"
    assert birth_date == "2000-02-29", "Should accept Feb 29 on leap years"
    
    with pytest.raises(ValueError, match=r"Invalid day 29 for month 2 and year 2001"):
        generate_pesel(2001, 2, 29)

def test_generate_pesel_century_encoding():
    pesel_1900s, _ = generate_pesel(1985, 3, 12, "M")  # Year 1985, March
    pesel_2000s, _ = generate_pesel(2005, 6, 25, "K")   # Year 2005, June

    # Check year encoding
    assert pesel_1900s[:2] == "85", "PESEL for 1900-1999 should contain year in first two digits"
    assert pesel_2000s[:2] == "05", "PESEL for 2000-2099 should contain year in first two digits"

    # Check month encoding
    assert pesel_1900s[2:4] == "03", "Month in PESEL for 1900-1999 should be normal"
    assert pesel_2000s[2:4] == "26", "Month in PESEL for 2000-2099 should have 20 added"

def test_generate_pesel_random_gender():
    pesel_mixed, _ = generate_pesel(1995, 8, 10)
    assert int(pesel_mixed[-2]) in range(10), "Random gender should still produce valid digit"

def test_generate_pesel_control_digit():
    pesel, _ = generate_pesel(1999, 12, 31, "K")
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = sum(int(pesel[i]) * weights[i] for i in range(10)) % 10
    control_digit = (10 - checksum) % 10
    assert int(pesel[-1]) == control_digit, "Control digit should be valid"

def test_personal_data_generator():
    generator = PersonalDataGeneratorBase(locale="pl")
    data = generator.generate_bulk(5)

    assert len(data) == 5, "Should generate exactly 5 records"
    for entry in data:
        parts = entry.split(",")
        assert len(parts) >= 5, "Entry should have at least 5 comma-separated parts"
        
        first_name, surname, gender, birth_date, pesel = parts[:5]
        
        assert first_name, "First name should not be empty"
        assert surname, "Surname should not be empty"
        assert gender in ("M", "K"), "Gender should be M or K"
        assert birth_date.count("-") == 2, "Birth date should be in YYYY-MM-DD format"
        assert len(pesel) == 11 and pesel.isdigit(), "PESEL should be 11 digits"

def test_pesel_with_random_params():
    pesel, birth_date = generate_pesel()
    assert len(pesel) == 11, "PESEL should be 11 characters long"
    assert pesel.isdigit(), "PESEL should contain only digits"
    assert birth_date, "Should generate random birth date"

def test_pesel_edge_centuries():
    # Test boundary years
    for year, expected_prefix in [(1800, "00"), (1899, "99"), 
                                 (1900, "00"), (1999, "99"),
                                 (2000, "00"), (2099, "99"),
                                 (2100, "00"), (2199, "99"),
                                 (2200, "00"), (2299, "99")]:
        pesel, _ = generate_pesel(year, 1, 1)
        assert pesel.startswith(expected_prefix), f"Year {year} should start with {expected_prefix}"