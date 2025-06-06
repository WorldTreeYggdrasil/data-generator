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
    output.write("    id SERIAL PRIMARY KEY,\n")
    output.write("    person_id VARCHAR(50) REFERENCES persons(id),\n")
    if "Street" in included_fields:
        output.write("    street VARCHAR(100),\n")
    if "City" in included_fields:
        output.write("    city VARCHAR(100),\n")
    if "Postal Code" in included_fields:
        output.write("    postal_code VARCHAR(10),\n")
    if "Country" in included_fields:
        output.write("    country VARCHAR(100),\n")
    output.write("    UNIQUE (person_id, street, city, postal_code, country)\n")
    output.write(");\n\n")
    
    # Debug output showing selected fields
    #output.write(f"-- Selected fields: {', '.join(sorted(included_fields)) or 'ALL'}\n\n")
    
    # Start transaction
    output.write("BEGIN;\n\n")
    
    # Insert data
    for i, record in enumerate(data, 1):
        # Debug record number
        #output.write(f"-- Record {i}\n")
        
        # Insert person with selected fields
        person_fields = []
        person_values = []
        for field in included_fields:
            # Handle field name variations
            field_lower = field.lower().replace(" ", "")
            if field_lower == "id":
                person_fields.append("id")
                val = record.get(field, '') or record.get('ID', '') or record.get('Id', '')
                person_values.append("NULL" if not val else f"'{val.replace("'", "''")}'")
            elif field_lower == "name":
                person_fields.append("name")
                val = record.get(field, '') or record.get('Name', '')
                person_values.append("NULL" if not val else f"'{val.replace("'", "''")}'")
            elif field_lower == "surname":
                person_fields.append("surname")
                val = record.get(field, '') or record.get('Surname', '')
                person_values.append("NULL" if not val else f"'{val.replace("'", "''")}'")
            elif field_lower in ["birthdate", "birth date"]:
                person_fields.append("birth_date")
                val = record.get(field, '') or record.get('Birth Date', '') or record.get('Birthdate', '')
                person_values.append("NULL" if not val else f"'{val.replace("'", "''")}'")
        
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
            # Handle field name variations
            field_lower = field.lower().replace(" ", "")
            if field_lower == "street":
                address_fields.append("street")
                val = record.get(field, '') or record.get('Street', '')
                address_values.append("NULL" if not val else f"'{val.replace("'", "''")}'")
            elif field_lower == "city":
                address_fields.append("city")
                val = record.get(field, '') or record.get('City', '')
                address_values.append("NULL" if not val else f"'{val.replace("'", "''")}'")
            elif field_lower in ["postalcode", "postal code"]:
                address_fields.append("postal_code")
                val = record.get(field, '') or record.get('Postal Code', '') or record.get('PostalCode', '')
                address_values.append("NULL" if not val else f"'{val.replace("'", "''")}'")
            elif field_lower == "country":
                address_fields.append("country")
                val = record.get(field, '') or record.get('Country', '')
                address_values.append("NULL" if not val else f"'{val.replace("'", "''")}'")
        
        if len(address_fields) > 1:  # More than just person_id
            output.write(f"INSERT INTO addresses ({', '.join(address_fields)}) VALUES (")
            output.write(", ".join(address_values))
            output.write(");\n")
        else:
            output.write("-- Skipping addresses insert (no selected fields)\n")
    
    # Commit transaction
    output.write("\nCOMMIT;\n")
    
    return output.getvalue()
