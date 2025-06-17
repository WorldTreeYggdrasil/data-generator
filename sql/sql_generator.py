import io
from typing import List, Dict

def escape_sql_value(val: str) -> str:
    """Zabezpiecza wartość przed SQL Injection przez podwajanie apostrofów.
    Jeśli wartość jest pusta lub None, zwraca NULL."""
    if val is None or val == '':
        return "NULL"
    # Zamień ' na '' zgodnie z SQL
    return "'" + val.replace("'", "''") + "'"

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

    # Zawsze dodaj "id"
    included_fields.add(normalized_field_map.get("id", "ID"))

    field_sql_map = {
        "id": "`id` VARCHAR(50) PRIMARY KEY",
        "birthdate": "`birth_date` DATE",
        "name": "`name` VARCHAR(100)",
        "surname": "`surname` VARCHAR(100)",
        "street": "`street` VARCHAR(100)",
        "city": "`city` VARCHAR(100)",
        "postalcode": "`postal_code` VARCHAR(10)",
        "country": "`country` VARCHAR(100)"
    }

    preferred_order = ["id", "birthdate", "name", "surname", "street", "city", "country", "postalcode"]

    output.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
    output.write(f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n")

    # Kolumny w CREATE TABLE według preferowanej kolejności
    for norm_field in preferred_order:
        if any(normalize(f) == norm_field for f in included_fields):
            output.write(f"    {field_sql_map[norm_field]},\n")

    # Usuń przecinek i zamknij definicję tabeli
    output.seek(output.tell() - 2)
    output.write("\n);\n\n")

    for record in data:
        columns = []
        values = []

        for norm_field in preferred_order:
            actual_field = next((f for f in included_fields if normalize(f) == norm_field), None)
            if actual_field:
                sql_field = field_sql_map[norm_field].split()[0]  # np. `id`
                val = record.get(actual_field, '')
                if val == '':
                    # Szukaj pod inną pisownią (np. normalizacja)
                    for k in record:
                        if normalize(k) == norm_field:
                            val = record[k]
                            break
                columns.append(sql_field)
                values.append(escape_sql_value(val))

        output.write(f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({', '.join(values)});\n")

    return output.getvalue()
