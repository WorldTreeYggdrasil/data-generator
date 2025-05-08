import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="baza_generator_danych"
)
cursor = conn.cursor()

plik_z_imionami = r"C:\IT\GitHub_Projects\data-generator\data\de\ImionaZenskie.txt"

cursor.execute("SELECT id FROM genders WHERE name = 'female'")
gender_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM countries WHERE language = 'de'")
country_id = cursor.fetchone()[0]

with open(plik_z_imionami, encoding="utf-8") as f:
    imiona = [line.strip() for line in f if line.strip()]

for imie in imiona:
    cursor.execute("""
        INSERT INTO first_names (name, gender_id, country_id)
        VALUES (%s, %s, %s)
    """, (imie, gender_id, country_id))

print(f"Dodano {len(imiona)} imion zenskich (DE) do tabeli first_names.")

conn.commit()
conn.close()
