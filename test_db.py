import os
from dotenv import load_dotenv
from mysql.connector import connect, Error

load_dotenv()

try:
    connection = connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    if connection.is_connected():
        print("✅ Połączenie z bazą danych działa!")
except Error as e:
    print("❌ Błąd połączenia:", e)
