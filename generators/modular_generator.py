import os
import random
import importlib
import logging
from typing import Dict, List, Optional
from .data_loader import DataLoader

class ModularDataGenerator:
    """Enhanced generator with dynamic data loading capabilities"""
    
    def __init__(self, locale: str = "pl"):
        self.locale = locale
        self.logger = logging.getLogger(__name__)
        self.data_loader = DataLoader(os.path.join(os.path.dirname(__file__), "../data/"))
        self.data_types = self.data_loader.discover_data_types(locale)
        self.parsed_postal_codes_data: List[Dict[str, str]] = []
        self._initialize_data()  # Nowa metoda do inicjalizacji i parsowania danych

        self.id_generator = self._load_id_generator()

    def _initialize_data(self):
        """
        Inicjalizuje i parsuje dane, w tym dane z kodów pocztowych.
        """
        if 'kody_pocztowe' in self.data_types:
            raw_postal_lines = self.data_types['kody_pocztowe']
            self.parsed_postal_codes_data = self._parse_postal_codes_data(raw_postal_lines)
            self.logger.info(f"Loaded and parsed {len(self.parsed_postal_codes_data)} postal code entries.")
        else:
            self.logger.warning("No 'kody_pocztowe.txt' found for the current locale.")

    def _parse_postal_codes_data(self, raw_lines: List[str]) -> List[Dict[str, str]]:
        """
        Parsuje surowe linie z pliku kodów pocztowych do listy słowników.
        Oczekiwany format: PNA;MIEJSCOWOŚĆ;ULICA;NUMERY;GMINA;POWIAT;WOJEWÓDZTWO
        """
        postal_codes_list = []
        for line in raw_lines:
            parts = line.split(';')
            if len(parts) >= 7:
                postal_code_entry = {
                    'pna': parts[0].strip(),
                    'miejscowosc': parts[1].strip(),
                    'ulica': parts[2].strip() if parts[2].strip() else None,
                    'numery': parts[3].strip() if parts[3].strip() else None,
                    'gmina': parts[4].strip(),
                    'powiat': parts[5].strip(),
                    'wojewodztwo': parts[6].strip()
                }
                postal_codes_list.append(postal_code_entry)
            else:
                self.logger.warning(f"Skipping malformed line in postal codes data: {line}")
        return postal_codes_list
        
    def _load_id_generator(self):
        """Dynamically load ID generator module if available"""
        module_path = f"generators.id_generators.pesel_{self.locale}"
        try:
            return importlib.import_module(module_path)
        except ImportError:
            self.logger.warning(f"No ID generator found for locale {self.locale}")
            return None

    def generate_record(self) -> Dict[str, str]:
        """Generate a single record with locale-aware name/surname matching and address"""
        record = {}
        is_female = random.choice([True, False])
        
        # Handle name selection
        if is_female:
            record["Name"] = random.choice(self.data_types.get("ImionaZenskie", []))
        else:
            record["Name"] = random.choice(self.data_types.get("ImionaMeskie", []))
            
        # Handle surname selection based on locale
        if self.locale == "de":
            # German uses combined surnames
            record["Surname"] = random.choice(self.data_types.get("Nazwiska", []))
        else:
            # Polish uses gender-specific surnames
            if is_female:
                record["Surname"] = random.choice(self.data_types.get("NazwiskaZenskie", []))
            else:
                record["Surname"] = random.choice(self.data_types.get("NazwiskaMeskie", []))
        
        # Add ID number and birth date
        if self.id_generator:
            id_number, birth_date = self.id_generator.generate_id_number()
            record["ID"] = id_number
            record["Birth Date"] = birth_date
        else:
            # Fallback random ID if no generator available
            record["ID"] = f"{random.randint(100000, 999999)}"
            record["Birth Date"] = f"{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

        # Generate address components
        if self.parsed_postal_codes_data:
            chosen_entry = random.choice(self.parsed_postal_codes_data)

            # Generowanie numeru domu z danych lub losowo
            house_number_suffix = ""
            if chosen_entry['numery']:
                if '-' in chosen_entry['numery']:  # Obsługa zakresów np. "1-10"
                    try:
                        start_num, end_num = map(int, chosen_entry['numery'].split('-'))
                        house_number_suffix = str(random.randint(start_num, end_num))
                    except ValueError:
                        house_number_suffix = chosen_entry['numery']  # W przypadku błędu, użyj surowego ciągu
                elif ',' in chosen_entry['numery']:  # Obsługa list np. "1,3,5"
                    possible_numbers = [n.strip() for n in chosen_entry['numery'].split(',')]
                    house_number_suffix = random.choice(possible_numbers)
                else:  # Konkretny numer
                    house_number_suffix = chosen_entry['numery']
            else:
                # Domyślny losowy numer, jeśli brak danych dla konkretnego wpisu
                house_number_suffix = str(random.randint(1, 150))

            # Użyj danych z pliku kody_pocztowe.txt dla wszystkich pól adresowych
            # Zmiana 1: Jeśli ulica jest pusta, użyj miejscowości + numeru domu
            record["Street"] = f"{chosen_entry['ulica']} {house_number_suffix}".strip() if chosen_entry['ulica'] else \
                f"{chosen_entry['miejscowosc']} {house_number_suffix}".strip()

            record["City"] = chosen_entry['miejscowosc']
            record["Postal Code"] = chosen_entry['pna'] if chosen_entry['pna'] else f"{random.randint(10, 99)}-{random.randint(100, 999)}"
            record["Gmina"] = chosen_entry['gmina']
            record["Powiat"] = chosen_entry['powiat']
            record["Wojewodztwo"] = chosen_entry['wojewodztwo']
            
            # Always include country from countries.txt if available
            if "countries" in self.data_types and self.data_types["countries"]:
                record["Country"] = random.choice(self.data_types["countries"])
            else:
                record["Country"] = "Poland" if self.locale == "pl" else "Germany"  # Default fallback based on locale

            # Zmiana 2: Usunięcie pola "Full Address"
            # record["Full Address"] = f"{record['Street']}, {record['Postal Code']} {record['City']}, {record['Gmina']}, {record['Powiat']}, {record['Wojewodztwo']}"
        else:
            # Fallback do starej logiki, jeśli brak danych o kodach pocztowych
            self.logger.warning("No postal code data available, generating simplified address.")
            if "streets" in self.data_types and self.data_types["streets"]:  # Sprawdź, czy lista nie jest pusta
                street = random.choice(self.data_types["streets"])
                house_num = random.randint(1, 150)
                record["Street"] = f"{street} {house_num}"
            else:  # Dodany else, aby w przypadku braku streets.txt nie dodawać pustego Street
                self.logger.warning("No 'streets.txt' data available for fallback.")

            if "cities" in self.data_types and self.data_types["cities"]:  # Sprawdź, czy lista nie jest pusta
                record["City"] = random.choice(self.data_types["cities"])
            else:
                self.logger.warning("No 'cities.txt' data available for fallback.")

            if "countries" in self.data_types and self.data_types["countries"]:  # Sprawdź, czy lista nie jest pusta
                record["Country"] = random.choice(self.data_types["countries"])
            else:
                self.logger.warning("No 'countries.txt' data available for fallback.")
            # Brak pełnych pól adresowych bez danych z kodów pocztowych (Postal Code, Gmina, Powiat, Wojewodztwo)

        return record

    def generate_bulk(self, quantity: int) -> List[Dict[str, str]]:
        """Generate multiple records"""
        return [self.generate_record() for _ in range(quantity)]

    def to_csv(self, data: List[Dict[str, str]], file_path: str, fields: List[str] = None):
        """Save generated data to CSV file with optional field filtering
        
        Args:
            data: List of records to save
            file_path: Output file path
            fields: List of field names to include (None for all fields)
        """
        if not data:
            raise ValueError("No data to save")
            
        # Use all fields if none specified
        headers = fields if fields else list(data[0].keys())
        
        # Verify all requested fields exist in data
        for field in headers:
            if field not in data[0]:
                raise ValueError(f"Field '{field}' not found in generated data")
                
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(",".join(headers) + "\n")  # Write header
            for record in data:
                f.write(",".join(str(record[h]) for h in headers) + "\n")
