import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.modular_generator import ModularDataGenerator

def main():
    print("Generating 10 Polish test records...")
    gen = ModularDataGenerator('pl')
    data = gen.generate_bulk(10)
    
    # Ensure test_output directory exists
    os.makedirs('test_output', exist_ok=True)
    output_path = 'test_output/polish_test_data.csv'
    
    gen.to_csv(data, output_path)
    print(f"Saved Polish test data to {output_path}")

if __name__ == "__main__":
    main()
