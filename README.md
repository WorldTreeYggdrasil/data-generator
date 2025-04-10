# Modular Data Generator

A flexible data generator that automatically adapts to available datasets with locale-specific handling.

## Features

- **Dynamic Data Loading**: Automatically discovers available locales and data types
- **Modular Architecture**: Easily extend with new data types and generators
- **Locale-aware Generation**: Handles locale-specific formats (e.g. Polish vs German names/IDs)
- **CSV Export**: Save generated data in standard CSV format
- **Test Data Generation**: Built-in scripts for generating test datasets

## Getting Started

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Generate test data:
```bash
# Polish test data
python tests/generate_polish_test_data.py

# German test data 
python tests/generate_german_test_data.py
```

Output files will be saved to `test_output/` directory.

## Adding New Data

1. Create a new locale directory in `data/` (e.g. `data/fr/`)
2. Add data files following conventions:
   - For locales with gender-specific surnames (like Polish):
     - `ImionaMeskie.txt` (Male first names)
     - `ImionaZenskie.txt` (Female first names)  
     - `NazwiskaMeskie.txt` (Male surnames)
     - `NazwiskaZenskie.txt` (Female surnames)
   - For locales with shared surnames (like German):
     - `ImionaMeskie.txt`
     - `ImionaZenskie.txt`
     - `Nazwiska.txt` (Shared surnames)

Example structures:
```
data/
  pl/  # Polish (gender-specific surnames)
    ImionaMeskie.txt
    ImionaZenskie.txt
    NazwiskaMeskie.txt  
    NazwiskaZenskie.txt

  de/  # German (shared surnames)
    ImionaMeskie.txt
    ImionaZenskie.txt
    Nazwiska.txt
```

## Adding ID Generators

1. Create a new module in `generators/id_generators/` following the pattern `pesel_[locale].py`
2. Implement the required interface:
```python
def generate_id_number(year=None, month=None, day=None, gender=None):
    """Returns tuple of (id_number, birth_date_as_YYYY-MM-DD)"""
    # Your implementation
    return id_number, birth_date
```
3. The system will automatically load generators matching the selected locale

Example implementations:
- `pesel_pl.py`: Polish PESEL numbers with gender encoding
- `pesel_de.py`: German-style ID numbers with birth date

## Architecture

```mermaid
graph TD
    A[main.py] --> B[DataLoader]
    A --> C[ModularDataGenerator]
    B --> D[data/ directory]
    C --> E[id_generators/]
    F[Test Scripts] --> C
    G[Output Files] --> C
```

Key Components:
- `DataLoader`: Discovers and loads locale-specific data files
- `ModularDataGenerator`: Creates records with proper locale handling
- `id_generators/`: Locale-specific ID generation implementations
- `tests/`: Scripts for generating test datasets

## Requirements

- Python 3.8+
- tkinter (usually included with Python)
