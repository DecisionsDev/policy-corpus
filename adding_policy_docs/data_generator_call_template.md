```python
from common.generic_data_generator import format_data_units

# paste this in the end of {policy_name}_data_generator.py file 
if __name__ == "__main__":
    sizes = [100, 1000]
    generator = {policy_name}DataGenerator()

    for size in sizes:
        df = generator.generate_test_dataset(size)
        data_units = format_data_units(size)
        df.to_csv(f'{policy_name}_test_dataset_{data_units}.csv', index=False)
```