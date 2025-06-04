import os
import logging
from typing import Dict, List

class DataLoader:
    """Handles dynamic discovery and loading of data files"""
    
    def __init__(self, base_data_path: str):
        self.base_data_path = base_data_path
        self.logger = logging.getLogger(__name__)
        
    def discover_locales(self) -> List[str]:
        """Discover available locales from data directory structure"""
        try:
            return [d for d in os.listdir(self.base_data_path) 
                   if os.path.isdir(os.path.join(self.base_data_path, d))]
        except Exception as e:
            self.logger.error(f"Error discovering locales: {e}")
            return []

    def discover_data_types(self, locale: str) -> Dict[str, List[str]]:
        """Discover available data types for a locale"""
        data_types = {}
        locale_path = os.path.join(self.base_data_path, locale)
        
        try:
            if os.path.exists(locale_path):
                for filename in os.listdir(locale_path):
                    if filename.endswith('.txt'):
                        data_type = filename.split('.')[0]
                        data_types[data_type] = self._load_file(locale_path, filename)
            return data_types
        except Exception as e:
            self.logger.error(f"Error discovering data types for {locale}: {e}")
            return {}

    def _load_file(self, locale_path: str, filename: str) -> List[str]:
        """Load data from a single file"""
        file_path = os.path.join(locale_path, filename)
        try:
            with open(file_path, encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return []
        except UnicodeDecodeError:
            self.logger.error(f"Decoding error: File {file_path} is not encoded in UTF-8 as expected.")
            return []
        except Exception as e:
            self.logger.error(f"Error loading {filename}: {e}")
            return []
