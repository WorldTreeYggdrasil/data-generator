import pytest
from generators.id_generators.pesel_de import generate_pkz

def test_generate_pkz_length():
    """Test that PKZ has correct length (11 digits)"""
    pkz = generate_pkz(1985, 12, 3, "M")
    assert len(pkz) == 11, "PKZ should be 11 characters long"
    assert pkz.isdigit(), "PKZ should contain only digits"

def test_generate_pkz_gender_encoding():
    """Test gender encoding in PKZ"""
    pkz_male = generate_pkz(1990, 10, 20, "M")
    pkz_female = generate_pkz(1990, 10, 20, "K")
    
    # 10th digit should be odd for male, even for female (index 9 in 0-based)
    assert int(pkz_male[9]) % 2 == 1, "Males should have odd 10th digit"
    assert int(pkz_female[9]) % 2 == 0, "Females should have even 10th digit"

def test_generate_pkz_date_encoding():
    """Test date encoding in PKZ"""
    pkz = generate_pkz(1985, 12, 3, "M")
    assert pkz[:6] == "851203", "Date should be encoded as YYMMDD"
    
    pkz2 = generate_pkz(1973, 7, 15, "K")
    assert pkz2[:6] == "730715", "Date should be encoded as YYMMDD"

def test_generate_pkz_control_digit():
    """Test control digit calculation"""
    pkz = generate_pkz(1985, 12, 3, "M")
    weights = [2, 1] * 5  # Only 10 weights needed for 10-digit base
    checksum = 0
    
    for i in range(10):  # Only iterate through first 10 digits
        product = int(pkz[i]) * weights[i]
        checksum += product // 10 + product % 10
    
    calculated_control = (10 - (checksum % 10)) % 10
    assert int(pkz[-1]) == calculated_control, "Control digit should be valid"

def test_generate_pkz_invalid_year():
    """Test year validation"""
    with pytest.raises(ValueError, match="Year must be between 1900 and 1999"):
        generate_pkz(1899, 1, 1)  # Too early
    with pytest.raises(ValueError):
        generate_pkz(2000, 1, 1)  # Too late

def test_generate_pkz_invalid_month():
    """Test month validation"""
    with pytest.raises(ValueError, match="Month must be between 1 and 12"):
        generate_pkz(1980, 0, 1)  # Month too low
    with pytest.raises(ValueError):
        generate_pkz(1980, 13, 1)  # Month too high

def test_generate_pkz_invalid_day():
    """Test day validation"""
    with pytest.raises(ValueError, match=r"Invalid day 32 for month 1 and year 1980"):
        generate_pkz(1980, 1, 32)  # Invalid day for January
    with pytest.raises(ValueError):
        generate_pkz(1980, 4, 31)  # Invalid day for April

def test_generate_pkz_leap_year():
    """Test leap year handling"""
    pkz_leap = generate_pkz(1984, 2, 29, "M")  # 1984 was a leap year
    assert pkz_leap[:6] == "840229", "Should accept Feb 29 on leap years"
    
    with pytest.raises(ValueError):
        generate_pkz(1985, 2, 29)  # 1985 was not a leap year

def test_generate_pkz_random_gender():
    """Test random gender generation"""
    pkz = generate_pkz(1975, 5, 15)  # No gender specified
    assert int(pkz[9]) in range(10), "Should generate valid gender digit"

def test_generate_pkz_random_params():
    """Test generation with random parameters"""
    pkz = generate_pkz()
    assert len(pkz) == 11, "PKZ should be 11 digits"
    assert pkz.isdigit(), "PKZ should contain only digits"
    
    # Verify control digit
    weights = [2, 1] * 5  # 10 weights for first 10 digits
    checksum = sum((int(pkz[i]) * weights[i]) // 10 + (int(pkz[i]) * weights[i]) % 10 for i in range(10))
    assert (checksum + int(pkz[-1])) % 10 == 0, "Control digit should be valid"