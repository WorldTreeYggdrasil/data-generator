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
    #output.write("BEGIN;\n\n")
    
    # Debug output showing complete record structure
    #output.write("-- FIRST RECORD STRUCTURE --\n")
    #for k, v in data[0].items():
    #   output.write(f"-- {k}: {v}\n")
    #output.write("\n")
    
    # Show all unique field names across all records
    all_fields = set()
    for record in data:
        all_fields.update(record.keys())
    #output.write(f"-- All unique fields found: {', '.join(all_fields)}\n\n")
    
    # Insert data
    for i, record in enumerate(data, 1):
        #output.write(f"-- Record {i} fields: {', '.join(record.keys())}\n")
        
        # Insert person with selected fields
        person_fields = []
        person_values = []
        for field in included_fields:
            # Handle field name variations with flexible matching
            field_lower = field.lower().replace(" ", "")
            if field_lower == "id":
                person_fields.append("id")
                val = next((record[k] for k in record if k.lower().replace(" ", "") == "id"), '')
                person_values.append("NULL" if not val else f"'{str(val).replace("'", "''")}'")
            elif field_lower == "name":
                person_fields.append("name")
                val = next((record[k] for k in record if k.lower().replace(" ", "") == "name"), '')
                person_values.append("NULL" if not val else f"'{str(val).replace("'", "''")}'")
            elif field_lower == "surname":
                person_fields.append("surname")
                val = next((record[k] for k in record if k.lower().replace(" ", "") == "surname"), '')
                person_values.append("NULL" if not val else f"'{str(val).replace("'", "''")}'")
            elif field_lower == "birthdate":
                person_fields.append("birth_date")
                val = record.get("BirthDate", "")
                person_values.append("NULL" if not val else f"'{str(val).replace("'", "''")}'")
                #output.write(f"-- Using standardized BirthDate field: {val}\n")
        
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
            # Handle field name variations with flexible matching
            field_lower = field.lower().replace(" ", "")
            if field_lower == "street":
                address_fields.append("street")
                val = next((record[k] for k in record if k.lower().replace(" ", "") == "street"), '')
                address_values.append("NULL" if not val else f"'{str(val).replace("'", "''")}'")
            elif field_lower == "city":
                address_fields.append("city")
                val = next((record[k] for k in record if k.lower().replace(" ", "") == "city"), '')
                address_values.append("NULL" if not val else f"'{str(val).replace("'", "''")}'")
            elif field_lower == "postalcode":
                address_fields.append("postal_code")
                val = record.get("PostalCode", "")
                address_values.append("NULL" if not val else f"'{str(val).replace("'", "''")}'")
                #output.write(f"-- Using standardized PostalCode field: {val}\n")
            elif field_lower == "country":
                address_fields.append("country")
                val = next((record[k] for k in record if k.lower().replace(" ", "") == "country"), '')
                address_values.append("NULL" if not val else f"'{str(val).replace("'", "''")}'")
        
        if len(address_fields) > 1:  # More than just person_id
            output.write(f"INSERT INTO addresses ({', '.join(address_fields)}) VALUES (")
            output.write(", ".join(address_values))
            output.write(");\n")
        else:
            output.write("-- Skipping addresses insert (no selected fields)\n")
    
    # Commit transaction
    output.write("\nCOMMIT;\n")
    
    return output.getvalue()
