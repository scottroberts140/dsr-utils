# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2026-04-18

### Added

* **Dynamic Reflection Utility**: Introduced safe_call, a general-purpose function for executing callables with automatic parameter filtering.
* **Signature Inspection**: Implemented inspect-based logic to programmatically identify valid keyword arguments for any Python function or class constructor.
* **Config Debugging Support**: Added a return mechanism for "rejected" parameters, allowing developers to identify extraneous configuration keys that do not match a function's signature.

### Changed

* **Pandas 2.0+ Compatibility**: Updated `is_string_datetime` and `infer_string_datetime_format` to support the `string` extension dtype in addition to standard `object` dtypes.
* **Heuristic Robustness**: Enhanced `is_string_datetime` to utilize `format="mixed"` for statistical evaluation of high-volume data profiling.
* **Hydration Robustness**: Updated utility patterns to support passing a mixture of fixed arguments and filtered variable keyword arguments (**kwargs).

### Fixed

* **Format Inference Logic**: Resolved an issue where `infer_string_datetime_format` returned `None` for standard ISO date and datetime strings by correcting dtype guard clauses.

## [1.4.0] - 2026-04-14

### Added

* **Deterministic Object Hashing**: Integrated joblib.hash logic into a new hashing module to generate unique fingerprints for DataFrames, NumPy arrays, and other complex Python objects.
* **Audit-Safe File Hashing**: Implemented chunked SHA-256 hashing for large raw data files, optimized to minimize memory overhead.
* **Integrity Validation Suite**: Added utilities to compare memory-resident data against stored checksums, providing the mathematical foundation for the orchestrator's "Run Capsule" architecture.

### Changed

* **Project Documentation**: Standardized all module-level and function-level docstrings to the NumPy format to ensure technical clarity for machine learning development.

## [1.3.0] - 2026-04-08

### Added

* **New Test Suites**: Comprehensive test coverage added for `tables.py`, `types.py`, `matplotlib.py`, and `strings.py`.
* **Enhanced Type Support**: `any_to_list` now supports `set`, `pd.Series`, `pd.Index`, and `np.ndarray` conversion.
* **NumPy-Style Documentation**: Standardized docstrings applied across all modules and tests for better IDE integration and clarity.

### Changed

* **Behavioral Change (any_to_list)**: Refactored `any_to_list` to preserve original data types (e.g., integers and floats) instead of implicitly casting them to strings.
* **List Handling**: `any_to_list` now returns a shallow copy of input lists to prevent accidental mutation of source data.
* **Dependency Update**: Minimum required versions updated to `pandas>=2.0.0` and `numpy>=2.0.0`.
* **Import Optimization**: Standardized all module imports to follow PEP 8 grouping using `isort`.

### Fixed

* **Date Inference Warning**: Resolved `UserWarning` in `is_string_datetime` by utilizing `format='mixed'` for improved parsing efficiency.
* **Renderer Stability**: Updated `matplotlib` utilities and test mocks to handle headless environments more robustly by ensuring `get_renderer` availability.

## [1.2.0] - 2026-04-08

### Added

* Comprehensive NumPy-style documentation across all modules (`matplotlib.py`, `tables.py`, etc.).
* Enhanced type hinting for layout metadata and rendering engine.

### Fixed

* Vertical scaling logic in `TablePage.calc_scaled_rect` to use height scaling instead of width.
* Standardized internal helper naming for better consistency in the rendering pipeline.
* `resolve_date_ambiguity` now correctly handles ISO-8601 dates (e.g., `2025-01-01`) by ensuring the first numeric part is <= 31 before identifying it as a day (EU format).

### Changed

* Refactored `TableColumn` and `Table` layout metrics calculation for better performance.

### Refactor

* Replaced manual leap year calculation with pandas built-in `.is_leap_year` property in `parse_datetime` and `parse_datetime_series`.

## [1.0.0] - 2026-02-08

### Breaking

* Version reset to 1.0.0 to reflect breaking changes and non-backward-compatible updates.

### Fixed

* `DataScale` AUTO selection now chooses the largest applicable unit (TB→GB→MB→KB→B).
* `convert_keys_to_case` now correctly recurses and converts nested keys.

### Tests

* Expanded formatting and strings test coverage for updated behavior.

## [0.0.4] - 2025-12-22

### Fixed

* Correct month cyclical encoding to use 0-based mapping `(month - 1)` for `sin_month` and `cos_month` to avoid December (`12`) overlapping with `0` (angle `2π`).

### Performance

* Replace per-index dictionary construction with `DataFrame.to_dict(orient='index')` in `parse_datetime_series`, significantly improving performance for large Series (millions of rows).

### Tests

* Updated expectations for month cyclical values; all tests passing (44/44). Datetime module coverage at 94%.

## [0.0.3] - 2025-12-22

### Added

* `parse_datetime()` and `parse_datetime_series()` with 26 datetime properties:
  * Date (15): `year`, `month`, `day`, `dayofweek`, `dayofyear`, `quarter`, `week`, `is_month_end`, `is_month_start`, `is_quarter_end`, `is_quarter_start`, `is_year_end`, `is_year_start`, `is_weekend`, `is_leap_year`
  * Time (3): `hour`, `minute`, `second`
  * Names (2): `day_name`, `month_name`
  * Cyclical (6): `sin_hour`, `cos_hour`, `sin_dayofweek`, `cos_dayofweek`, `sin_month`, `cos_month`

### Notes

* Vectorized Series operations via `.dt` accessor for better performance.
