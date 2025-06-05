import io
from typing import List, Dict

def generate_sql(data: List[Dict[str, str]], locale: str) -> str:
    """Generate SQL output with proper relational structure
    
    Args:
        data: List of generated records
        locale: Locale code (e.g. 'pl', 'de')
        
    Returns:
        SQL string with CREATE TABLE and INSERT statements
    """
    output = io.StringIO()
    
    # Create tables
    output.write("CREATE TABLE IF NOT EXISTS persons (\n")
    output.write("    id VARCHAR(50) PRIMARY KEY,\n")
    output.write("    name VARCHAR(100),\n")
    output.write("    surname VARCHAR(100),\n")
    output.write("    birth_date DATE\n")
    output.write(");\n\n")
    
    output.write("CREATE TABLE IF NOT EXISTS addresses (\n")
    output.write("    person_id VARCHAR(50) REFERENCES persons(id),\n")
    output.write("    street VARCHAR(100),\n")
    output.write("    city VARCHAR(100),\n")
    output.write("    postal_code VARCHAR(10),\n")
    output.write("    country VARCHAR(100),\n")
    output.write("    PRIMARY KEY (person_id)\n")
    output.write(");\n\n")
    
    # Insert data
    for record in data:
        # Insert person
        output.write("INSERT INTO persons (id, name, surname, birth_date) VALUES (")
        output.write(f"'{record.get('ID', '')}', ")
        output.write(f"'{record.get('Name', '')}', ")
        output.write(f"'{record.get('Surname', '')}', ")
        output.write(f"'{record.get('Birth Date', '')}'")
        output.write(");\n")
        
        # Insert address
        output.write("INSERT INTO addresses (person_id, street, city, postal_code, country) VALUES (")
        output.write(f"'{record.get('ID', '')}', ")
        output.write(f"'{record.get('Street', '')}', ")
        output.write(f"'{record.get('City', '')}', ")
        output.write(f"'{record.get('Postal Code', '')}', ")
        output.write(f"'{record.get('Country', '')}'")
        output.write(");\n")
    
    return output.getvalue()
