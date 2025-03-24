import os
import random
import importlib

class PersonalDataGeneratorBase:
    def __init__(self, locale="pl"):
        self.locale = locale
        self.data_path = os.path.join(os.path.dirname(__file__), f"../data/{locale}/")
        self.load_data()
        
        if self.locale == "pl":
            self.id_generator = importlib.import_module("generators.id_generators.pesel_pl")
        elif self.locale == "de":
            self.id_generator = importlib.import_module("generators.id_generators.pkz_de")
        else:
            self.id_generator = None

    def load_data(self):
        """Ładuje dane imion i nazwisk dla wybranego kraju"""
        try:
            if self.locale in {"pl", "de"}:
                self.male_names = self._load_file("ImionaMeskie.txt")
                self.female_names = self._load_file("ImionaZenskie.txt")
                self.male_surnames = self._load_file("NazwiskaMeskie.txt")
                self.female_surnames = self._load_file("NazwiskaZenskie.txt")
            else:
                raise ValueError(f"Nieobsługiwana lokalizacja: {self.locale}")
        except FileNotFoundError as e:
            print(f"Error: Brak pliku z danymi dla {self.locale} - {e}")

    def _load_file(self, filename):
        """Pomocnicza metoda do wczytywania plików"""
        file_path = os.path.join(self.data_path, filename)
        with open(file_path, encoding="utf-8") as f:
            return f.read().splitlines()

    def generate_bulk(self, quantity):
        """Generuje wiele rekordów losowych danych osobowych"""
        generated_data = []
        for _ in range(quantity):
            is_male = random.choice([True, False])
            first_name = random.choice(self.male_names if is_male else self.female_names)
            surname = random.choice(self.male_surnames if is_male else self.female_surnames)
            gender = "M" if is_male else "K"
            
            id_number, birth_date = self.generate_id_number(gender)

            generated_data.append(f"{first_name},{surname},{gender},{birth_date},{id_number}")
        return generated_data

    def generate_id_number(self, gender=None):
        """Generuje numer identyfikacyjny (PESEL dla PL, PKZ dla DE) i zwraca datę urodzenia"""
        if self.id_generator:
            return self.id_generator.generate_id_number(gender=gender)  
        else:
            raise NotImplementedError(f"Nie zaimplementowano generowania numeru dla lokalizacji {self.locale}")

    def to_csv(self, data, file_path):
        """Zapisuje dane do pliku CSV"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("First Name,Surname,Gender,Birth Date,ID Number\n")  # CSV header
            f.write("\n".join(data))
