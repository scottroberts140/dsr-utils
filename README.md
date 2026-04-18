# dsr-utils

[![PyPI version](https://img.shields.io/pypi/v/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![Python versions](https://img.shields.io/pypi/pyversions/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![License](https://img.shields.io/pypi/l/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![Changelog](https://img.shields.io/badge/changelog-available-blue.svg)](https://github.com/scottroberts140/dsr-utils/releases)

Utility functions and helpers for common data science tasks, including datetime parsing, formatting, tables, and plotting helpers.

**Version 1.6.0**: Enhanced the **reflection module** with a manual bypass mode (`valid_params`) to support strict parameter filtering for functions utilizing `**kwargs` passthrough.

## Features

- **Datetime utilities**: Parse and enrich timestamps with vectorized pandas integration.
- **Formatting utilities**: Numeric, currency, percentage, and datetime formatters.
- **Table helpers**: High-precision layout engine with pagination support.
- **Matplotlib helpers**: Headless-friendly bounding box and renderer utilities.
- **String utilities**: Recursive case conversion (snake, pascal, camel, etc.).
- **Type utilities**: Robust standardization of scalars and collections into flat lists.
- **Hashing Utilities**: Generate deterministic fingerprints for pandas DataFrames, NumPy arrays, and large files using memory-efficient SHA-256 and joblib hashing.
- **Reflection Utilities**: Programmatically inspect function signatures and safely execute callables by filtering incompatible keyword arguments.

## Installation

```bash
pip install dsr-utils
```

## Usage

### General Usage

```python
import pandas as pd
from dsr_utils.datetime import parse_datetime
from dsr_utils.formatting import FloatFormat
from dsr_utils.tables import Table, TableColumn, TableColumnStyle, render_table

# Datetime parsing with Pandas 2.0+ mixed-format support
ts = pd.Timestamp("2025-10-01 12:34:56")
# (Usage of parse_datetime utility here)

# Formatting utilities
fmt = FloatFormat(precision=2)
print(fmt.format_value(1234.567))

# Table helpers (v1.3.0 constructor requirements)
df = pd.DataFrame({"Metric": ["Trips"], "Value": ["1,200"]})
style = TableColumnStyle()
table = Table(
    data=df,
    max_table_height=0.5,
    mid_x=0.5,
    top_y=0.8,
    fontsize=11,
    columns={
        "Metric": TableColumn(detail_style=style, header_style=style),
        "Value": TableColumn(detail_style=style, header_style=style)
    }
)
```

### Data Integrity & Hashing

```python
import pandas as pd
from dsr_utils.hashing import calculate_object_hash, calculate_file_hash
from pathlib import Path

# Generate a deterministic hash for a DataFrame
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df_hash = calculate_object_hash(df)
print(f"DataFrame Fingerprint: {df_hash}")

# Calculate hash for a raw data file without loading it entirely into memory
# Ideal for large CSVs on memory-constrained systems like a Mac-mini
file_path = Path("data/raw/adult.csv")
file_hash = calculate_file_hash(file_path)
print(f"File Fingerprint: {file_hash}")
```

### Dynamic Function Execution

```python
from dsr_utils.reflection import safe_call

def process_data(data, mode="fast", verbose=False):
    return f"Processing {data} in {mode} mode"

# A dictionary containing both valid and invalid parameters
raw_config = {
    "mode": "thorough",
    "verbose": True,
    "unsupported_param": "ignore_me"
}

# safe_call filters the config and returns the result + rejected keys
result, rejected = safe_call(process_data, raw_config, data="MyDataset")

print(result)            # Output: Processing MyDataset in thorough mode
print(rejected.keys())   # Output: dict_keys(['unsupported_param'])
```

### Advanced Reflection: Manual Filtering

For functions that use `**kwargs` in their signature (like `json.load` or `pd.read_parquet`), standard reflection cannot identify invalid parameters. In these cases, you can provide an explicit set of `valid_params` to bypass reflection and enforce strict filtering.

```python
from dsr_utils.reflection import safe_call

# Example: pd.read_parquet has **kwargs, so we provide a strict set
PARQUET_READ_PARAMS = {"path", "engine", "columns", "storage_options"}

raw_config = {
    "columns": ["id", "value"],
    "fake_param": "invalid"
}

# safe_call uses valid_params as the ground truth instead of inspection
result, rejected = safe_call(
    pd.read_parquet, 
    raw_config, 
    valid_params=PARQUET_READ_PARAMS, 
    path="data.parquet"
)

print(rejected)  # Output: {'fake_param': 'invalid'}
```

**Note on Conflict Resolution**: If a parameter in your config dictionary conflicts with a value passed via `**fixed_kwargs`, the value in `fixed_kwargs` takes precedence, and the original value is moved to the `rejected` dictionary for visibility.

## Requirements

- Python >= 3.10
- numpy >= 2.0.0
- pandas >= 2.0.0
- joblib >= 1.4.0
- matplotlib (required for matplotlib helpers)

## License

MIT License - see LICENSE file for details
