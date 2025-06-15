from flask import Flask, request, jsonify, make_response, send_from_directory
from desktop_gui.app import run_desktop_app
from generators.modular_generator import ModularDataGenerator
from generators.data_loader import DataLoader
import os
import io
import csv
import argparse
from mysql.connector import connect, Error
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='.')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'webui.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/locales')
def get_locales():
    base_data_path = os.path.join(os.path.dirname(__file__), "data")
    data_loader = DataLoader(base_data_path)
    locales = data_loader.discover_locales()
    return jsonify(locales)

@app.route('/preview-sql', methods=['POST'])
def preview_sql():
    data = request.get_json()
    locale = data.get('locale')
    quantity = int(data.get('quantity'))
    fields = data.get('fields', [])

    try:
        generator = ModularDataGenerator(locale)
        generated_data = generator.generate_bulk(quantity)

        from sql.sql_generator import generate_sql
        sql_content = generate_sql(generated_data, locale, fields, table_name="generated_people_PREVIEW")

        return jsonify({
            'sql': sql_content
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_data():
    data = request.get_json()
    locale = data.get('locale')
    quantity = int(data.get('quantity'))
    fields = data.get('fields', [])
    format = data.get('format', 'csv')
    confirm = data.get('confirm', False)

    try:
        generator = ModularDataGenerator(locale)
        generated_data = generator.generate_bulk(quantity)

        if format == 'sql':
            if not confirm:
                return jsonify({
                    'message': '⚠️ Confirmation required before saving to database.',
                    'requires_confirmation': True
                }), 400

            from sql.sql_generator import generate_sql

            try:
                connection = connect(
                    host=os.getenv('DB_HOST'),
                    database=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD')
                )

                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SHOW TABLES LIKE 'generated_people_%'")
                    existing_tables = cursor.fetchall()
                    existing_numbers = []

                    for table in existing_tables:
                        try:
                            suffix = int(table[0].split('_')[-1])
                            existing_numbers.append(suffix)
                        except ValueError:
                            pass

                    next_number = max(existing_numbers, default=0) + 1
                    new_table_name = f"generated_people_{next_number}"

                    sql_content = generate_sql(generated_data, locale, fields, table_name=new_table_name)

                    for stmt in sql_content.split(';'):
                        stmt = stmt.strip()
                        if stmt:
                            try:
                                cursor.execute(stmt)
                            except Error as e:
                                connection.rollback()
                                return jsonify({
                                    'error': f'SQL execution error: {str(e)}',
                                    'sql_statement': stmt
                                }), 500

                    connection.commit()
                    cursor.close()
                    connection.close()
                    return jsonify({
                        'message': f'✅ Data successfully saved to table `{new_table_name}`.'
                    }), 200

            except Error as db_error:
                print(f"❌ Database connection error: {db_error}")
                sql_content = generate_sql(generated_data, locale, fields)
                response = make_response(sql_content)
                response.headers['Content-Disposition'] = f'attachment; filename=generated_data_{locale}.sql'
                response.headers['Content-type'] = 'application/sql'
                return response

        else:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(fields)

            for record in generated_data:
                row = []
                for field in fields:
                    if field in record:
                        row.append(record[field])
                        continue
                    field_lower = field.lower().replace(" ", "")
                    for actual_field in record:
                        if field_lower == actual_field.lower().replace(" ", ""):
                            row.append(record[actual_field])
                            break
                    else:
                        row.append('')
                writer.writerow(row)

            response = make_response(output.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename=generated_data_{locale}.csv'
            response.headers['Content-type'] = 'text/csv'
            return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data Generator Application')
    parser.add_argument('--gui', action='store_true', help='Run desktop GUI interface')
    args = parser.parse_args()

    if args.gui:
        run_desktop_app()
    else:
        app.run(host='0.0.0.0', port=5000)