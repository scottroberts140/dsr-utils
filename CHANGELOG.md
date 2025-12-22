# Changelog

All notable changes to this project will be documented in this file.

## [0.0.4] - 2025-12-22
### Fixed
- Correct month cyclical encoding to use 0-based mapping `(month - 1)` for `sin_month` and `cos_month` to avoid December (`12`) overlapping with `0` (angle `2π`).

### Performance
- Replace per-index dictionary construction with `DataFrame.to_dict(orient='index')` in `parse_datetime_series`, significantly improving performance for large Series (millions of rows).

### Tests
- Updated expectations for month cyclical values; all tests passing (44/44). Datetime module coverage at 94%.

## [0.0.3] - 2025-12-22
### Added
- `parse_datetime()` and `parse_datetime_series()` with 26 datetime properties:
  - Date (15): `year`, `month`, `day`, `dayofweek`, `dayofyear`, `quarter`, `week`, `is_month_end`, `is_month_start`, `is_quarter_end`, `is_quarter_start`, `is_year_end`, `is_year_start`, `is_weekend`, `is_leap_year`
  - Time (3): `hour`, `minute`, `second`
  - Names (2): `day_name`, `month_name`
  - Cyclical (6): `sin_hour`, `cos_hour`, `sin_dayofweek`, `cos_dayofweek`, `sin_month`, `cos_month`

### Notes
- Vectorized Series operations via `.dt` accessor for better performance.
