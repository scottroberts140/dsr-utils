# dsr-utils

[![PyPI version](https://img.shields.io/pypi/v/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![Python versions](https://img.shields.io/pypi/pyversions/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![License](https://img.shields.io/pypi/l/dsr-utils.svg?cacheSeconds=300)](https://pypi.org/project/dsr-utils/)
[![Changelog](https://img.shields.io/badge/changelog-available-blue.svg)](https://github.com/scottroberts140/dsr-utils/releases)

Utility functions and helpers for common data science tasks, including datetime parsing, formatting, tables, and plotting helpers.

**Version 1.0.0**: This release is breaking and not backward-compatible with prior 0.x versions.

## Features

- **Datetime utilities**: Parse and enrich timestamps with pandas integration.
- **Formatting utilities**: Numeric, currency, percentage, and datetime formatters.
- **Table helpers**: Lightweight table definitions and rendering helpers.
- **Matplotlib helpers**: Bounding box utilities for layout and export.
- **String utilities**: Text processing and manipulation helpers.
- **Type utilities**: Lightweight type conversion helpers.

## Installation

```bash
pip install dsr-utils
```

## Usage

```python
from dsr_utils import (
	parse_datetime,
	DateTimeFormat,
	FloatFormat,
	Table,
	TableColumn,
	render_table,
)

# Datetime parsing (pandas integration)
ts = parse_datetime("2025-10-01 12:34:56")

# Formatting utilities
fmt = FloatFormat(precision=2)
print(fmt.format_value(1234.567))

# Date/time formatting
dt_fmt = DateTimeFormat(date_format="%Y-%m-%d", time_format="%H:%M")
print(dt_fmt.format_value(ts))

# Table helpers
table = Table(
	columns=[TableColumn("metric"), TableColumn("value")],
	rows=[{"metric": "rows", "value": 1234}],
)
render_table(table)
```

## Requirements

- Python >= 3.10
- numpy
- pandas (required for datetime utilities)
- matplotlib (required for matplotlib helpers)

## License

MIT License - see LICENSE file for details
