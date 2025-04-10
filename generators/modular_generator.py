import os
import random
import importlib
import logging
from typing import Dict, List
from .data_loader import DataLoader

class ModularDataGenerator:
    """Enhanced generator with dynamic data loading capabilities"""
    
    def __init__(self, locale: str = "pl"):
        self.locale = locale
        self.logger = logging.getLogger(__name__)
        self.data_loader = DataLoader(os.path.join(os.path.dirname(__file__), "../data/"))
        self.data_types = self.data_loader.discover_data_types(locale)
        self.id_generator = self._load_id_generator()
        
    def _load_id_generator(self):
        """Dynamically load ID generator module if available"""
        module_path = f"generators.id_generators.pesel_{self.locale}"
        try:
            return importlib.import_module(module_path)
        except ImportError:
            self.logger.warning(f"No ID generator found for locale {self.locale}")
            return None

    def generate_record(self) -> Dict[str, str]:
        """Generate a single record with locale-aware name/surname matching"""
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
        
        # Add ID number and birth date if generator available
        if self.id_generator:
            id_number, birth_date = self.id_generator.generate_id_number()
            record["ID"] = id_number
            record["Birth Date"] = birth_date
            
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
