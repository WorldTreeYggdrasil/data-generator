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
        """Generate a single record using available data types"""
        record = {}
        for data_type, values in self.data_types.items():
            if values:  # Only include if we have data
                record[data_type] = random.choice(values)
        
        # Add ID number if generator available
        if self.id_generator:
            id_number, birth_date = self.id_generator.generate_id_number()
            record["id_number"] = id_number
            record["birth_date"] = birth_date
            
        return record

    def generate_bulk(self, quantity: int) -> List[Dict[str, str]]:
        """Generate multiple records"""
        return [self.generate_record() for _ in range(quantity)]

    def to_csv(self, data: List[Dict[str, str]], file_path: str):
        """Save generated data to CSV file"""
        if not data:
            raise ValueError("No data to save")
            
        headers = list(data[0].keys())
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(",".join(headers) + "\n")  # Write header
            for record in data:
                f.write(",".join(str(record[h]) for h in headers) + "\n")
