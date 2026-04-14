# dsr-utils

[![PyPI version](https://img.shields.io/pypi/v/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![Python versions](https://img.shields.io/pypi/pyversions/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![License](https://img.shields.io/pypi/l/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![Changelog](https://img.shields.io/badge/changelog-available-blue.svg)](https://github.com/scottroberts140/dsr-utils/releases)

Utility functions and helpers for common data science tasks, including datetime parsing, formatting, tables, and plotting helpers.

**Version 1.4.0**: This release introduces a comprehensive **hashing module** for deterministic object and file-level integrity verification. It provides the "Source of Truth" foundation for audit-safe machine learning pipelines.

## Features

- **Datetime utilities**: Parse and enrich timestamps with vectorized pandas integration.
- **Formatting utilities**: Numeric, currency, percentage, and datetime formatters.
- **Table helpers**: High-precision layout engine with pagination support.
- **Matplotlib helpers**: Headless-friendly bounding box and renderer utilities.
- **String utilities**: Recursive case conversion (snake, pascal, camel, etc.).
- **Type utilities**: Robust standardization of scalars and collections into flat lists.
- **Hashing Utilities**: Generate deterministic fingerprints for pandas DataFrames, NumPy arrays, and large files using memory-efficient SHA-256 and joblib hashing.

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

## Requirements

- Python >= 3.10
- numpy >= 2.0.0
- pandas >= 2.0.0
- joblib >= 1.4.0
- matplotlib (required for matplotlib helpers)

## License

MIT License - see LICENSE file for details
