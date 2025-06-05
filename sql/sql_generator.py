import io
from typing import List, Dict

def generate_sql(data: List[Dict[str, str]], locale: str, fields: List[str] = None) -> str:
    """Generate SQL output with proper relational structure
    
    Args:
        data: List of generated records
        locale: Locale code (e.g. 'pl', 'de')
        fields: List of field names to include (None for all fields)
        
    Returns:
        SQL string with CREATE TABLE and INSERT statements
    """
    output = io.StringIO()
    
    # Determine which fields to include
    all_fields = set()
    for record in data:
        all_fields.update(record.keys())
    
    if fields:
        # Normalize field names and validate
        included_fields = set()
        for field in fields:
            # Match field names case-insensitively
            matched = False
            for actual_field in all_fields:
                if field.lower() == actual_field.lower():
                    included_fields.add(actual_field)
                    matched = True
                    break
            if not matched:
                raise ValueError(f"Field '{field}' not found in generated data")
    else:
        included_fields = all_fields

    # Create tables with only requested fields
    output.write("CREATE TABLE IF NOT EXISTS persons (\n")
    output.write("    id VARCHAR(50) PRIMARY KEY,\n")
    if "Name" in included_fields:
        output.write("    name VARCHAR(100),\n")
    if "Surname" in included_fields:
        output.write("    surname VARCHAR(100),\n")
    if "Birth Date" in included_fields:
        output.write("    birth_date DATE\n")
    output.write(");\n\n")
    
    output.write("CREATE TABLE IF NOT EXISTS addresses (\n")
    output.write("    person_id VARCHAR(50) REFERENCES persons(id),\n")
    if "Street" in included_fields:
        output.write("    street VARCHAR(100),\n")
    if "City" in included_fields:
        output.write("    city VARCHAR(100),\n")
    if "Postal Code" in included_fields:
        output.write("    postal_code VARCHAR(10),\n")
    if "Country" in included_fields:
        output.write("    country VARCHAR(100),\n")
    output.write("    PRIMARY KEY (person_id)\n")
    output.write(");\n\n")
    
    # Debug output showing selected fields
    #output.write(f"-- Selected fields: {', '.join(sorted(included_fields)) or 'ALL'}\n\n")
    
    # Insert data
    for i, record in enumerate(data, 1):
        # Debug record number
        #output.write(f"-- Record {i}\n")
        
        # Insert person with selected fields
        person_fields = []
        person_values = []
        for field in included_fields:
            if field == "ID":
                person_fields.append("id")
                person_values.append(f"'{record.get('ID', '')}'")
            elif field == "Name":
                person_fields.append("name")
                person_values.append(f"'{record.get('Name', '')}'")
            elif field == "Surname":
                person_fields.append("surname")
                person_values.append(f"'{record.get('Surname', '')}'")
            elif field == "Birth Date":
                person_fields.append("birth_date")
                person_values.append(f"'{record.get('Birth Date', '')}'")
        
        if person_fields:
            output.write(f"INSERT INTO persons ({', '.join(person_fields)}) VALUES (")
            output.write(", ".join(person_values))
            output.write(");\n")
        else:
            output.write("-- Skipping persons insert (no selected fields)\n")
        
        # Insert address with selected fields
        address_fields = []
        address_values = []
        
        # Always include person_id if ID is included
        if "ID" in included_fields:
            address_fields.append("person_id")
            address_values.append(f"'{record.get('ID', '')}'")
            
        for field in included_fields:
            if field == "Street":
                address_fields.append("street")
                address_values.append(f"'{record.get('Street', '')}'")
            elif field == "City":
                address_fields.append("city")
                address_values.append(f"'{record.get('City', '')}'")
            elif field == "Postal Code":
                address_fields.append("postal_code")
                address_values.append(f"'{record.get('Postal Code', '')}'")
            elif field == "Country":
                address_fields.append("country")
                address_values.append(f"'{record.get('Country', '')}'")
        
        if len(address_fields) > 1:  # More than just person_id
            output.write(f"INSERT INTO addresses ({', '.join(address_fields)}) VALUES (")
            output.write(", ".join(address_values))
            output.write(");\n")
        else:
            output.write("-- Skipping addresses insert (no selected fields)\n")
    
    return output.getvalue()
