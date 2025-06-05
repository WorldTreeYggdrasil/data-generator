from flask import Flask, request, jsonify, make_response, send_from_directory
from desktop_gui.app import run_desktop_app
from generators.modular_generator import ModularDataGenerator
from generators.data_loader import DataLoader
import os
import io
import csv
import argparse
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()



app = Flask(__name__, static_folder='.')

@app.route('/')
def serve_index():
    """Serve the main web UI page"""
    return send_from_directory('.', 'webui.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the root directory"""
    return send_from_directory('.', path)

@app.route('/locales')
def get_locales():
    """API endpoint to get list of available locales
    
    Returns:
        JSON array of locale codes (e.g. ['pl', 'de'])
    """
    base_data_path = os.path.join(os.path.dirname(__file__), "data")
    data_loader = DataLoader(base_data_path)
    locales = data_loader.discover_locales()
    return jsonify(locales)

@app.route('/generate', methods=['POST'])
def generate_data():
    """API endpoint to generate data in requested format

    Request body (JSON):
    - locale: locale code (e.g. 'pl')
    - quantity: number of records to generate
    - fields: array of field names to include
    - format: output format ('csv' or 'sql')

    Returns:
        File attachment or DB insert depending on format
    """
    from mysql.connector import connect, Error

    data = request.get_json()
    locale = data.get('locale')
    quantity = int(data.get('quantity'))
    fields = data.get('fields', [])
    format = data.get('format', 'csv')

    try:
        generator = ModularDataGenerator(locale)
        generated_data = generator.generate_bulk(quantity)

        if format == 'sql':
            from sql.sql_generator import generate_sql
            sql_content = generate_sql(generated_data, locale, fields)

            try:
                connection = connect(
                    host=os.getenv('DB_HOST'),
                    database=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD')
                )


                if connection.is_connected():
                    cursor = connection.cursor()
                    for stmt in sql_content.split(';'):
                        stmt = stmt.strip()
                        if stmt:
                            cursor.execute(stmt)
                    connection.commit()
                    cursor.close()
                    connection.close()
                    return jsonify({'message': '✅ Dane zostały zapisane w bazie danych.'}), 200

            except Error as db_error:
                print(f"❌ Nie można połączyć z bazą: {db_error}")
                # Jeśli baza nie działa — generujemy plik SQL
                response = make_response(sql_content)
                response.headers['Content-Disposition'] = f'attachment; filename=generated_data_{locale}.sql'
                response.headers['Content-type'] = 'application/sql'
                return response

        else:
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(fields)
            for record in generated_data:
                row = [record.get(field, '') for field in fields]
                writer.writerow(row)

            # Prepare CSV response
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
