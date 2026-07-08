# Sync History Log

This log tracks all sync runs from upstream (`as_upstream` branch) into our active working branch (`ebt` or `main`).

## [2026-07-07] Refined EBT Integration
- **Source branch**: `version-zero` (commit `5578c8d0`)
- **Target branch**: `ebt`
- **Method**: Programmatic extraction of unique assets and programmatic injection of EBT UI wrapper elements into clean `as_upstream` Sutta HTML files. This prevents overwriting newer Sutta text updates and dictionary databases with outdated/buggy versions from `version-zero`.
- **Status**: Completed (100% Sutta coverage verified)
