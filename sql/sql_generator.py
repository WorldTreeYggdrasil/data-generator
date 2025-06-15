import io
from typing import List, Dict

def generate_sql(data: List[Dict[str, str]], locale: str, fields: List[str] = None, table_name: str = "generated_people") -> str:
    output = io.StringIO()

    all_fields = set()
    for record in data:
        all_fields.update(record.keys())

    def normalize(f):
        return f.lower().replace(" ", "")

    normalized_field_map = {normalize(f): f for f in all_fields}

    if fields:
        included_fields = set()
        for field in fields:
            norm = normalize(field)
            if norm in normalized_field_map:
                included_fields.add(normalized_field_map[norm])
            else:
                raise ValueError(f"Field '{field}' not found in generated data")
    else:
        included_fields = all_fields

    included_fields.add(normalized_field_map.get("id", "ID"))

    # Mapa pól i ich typów SQL
    field_sql_map = {
        "id": "id VARCHAR(50) PRIMARY KEY",
        "birthdate": "birth_date DATE",
        "name": "name VARCHAR(100)",
        "surname": "surname VARCHAR(100)",
        "street": "street VARCHAR(100)",
        "city": "city VARCHAR(100)",
        "postalcode": "postal_code VARCHAR(10)",
        "country": "country VARCHAR(100)"
    }

    # Preferowana kolejność kolumn
    preferred_order = ["id", "birthdate", "name", "surname", "street", "city", "country", "postalcode"]

    output.write(f"DROP TABLE IF EXISTS {table_name};\n")
    output.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")

    # Wypisz kolumny CREATE TABLE w preferowanej kolejności,
    # ale tylko jeśli są zaznaczone w included_fields
    for norm_field in preferred_order:
        if any(normalize(f) == norm_field for f in included_fields):
            output.write(f"    {field_sql_map[norm_field]},\n")

    # Usuń ostatni przecinek i nową linię, zamknij nawias
    output.seek(output.tell() - 2)
    output.write("\n);\n\n")

    for record in data:
        columns = []
        values = []

        # Przy generowaniu INSERT zachowaj tę samą kolejność
        for norm_field in preferred_order:
            actual_field = next((f for f in included_fields if normalize(f) == norm_field), None)
            if actual_field:
                sql_field = field_sql_map[norm_field].split()[0]  # nazwa kolumny bez typu
                val = record.get(actual_field, '')
                if not val:
                    for k in record:
                        if normalize(k) == norm_field:
                            val = record[k]
                            break
                columns.append(sql_field)
                values.append(f"'{val}'")

        output.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")

    return output.getvalue()
