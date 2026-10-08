# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [v1.3.0] - 2026-10-08

### Added
- Added a pytest plugin.
- Added a changelog to record release history and notable changes.

### Changed
- Split the implementation into multiple modules.
- Improved performance when processing large changesets.
- Replaced MkDocs with ProperDocs for documentation.

## [v1.2.3] - 2026-03-05

### Fixed
- Fixed a race condition affecting parallel test execution.

## [v1.2.2] - 2026-03-05

### Fixed
- Tracked missing files in known reference-data sets.

## [v1.2.1] - 2026-03-04

### Fixed
- Fixed Windows-specific issues.
- Added `sys-prefix` to the default configuration.

## [v1.2.0] - 2026-03-04

### Added
- Added the `known` option for reference-data handling.

### Changed
- Updated copyright metadata.

## [v1.1.1] - 2025-06-17

### Changed
- Updated the project environment and CI compatibility.

### Fixed
- Attempted to address a reported issue affecting the runtime environment.

## [v1.1.0] - 2025-06-13

### Added
- Added support for ignoring whitespace differences during comparisons.

## [v1.0.2] - 2025-06-12

### Fixed
- Fixed Windows newline handling in comparisons.

## [v1.0.1] - 2025-06-12

### Added
- Added `add_excludes` and `rm_excludes` support.

## [v1.0.0] - 2025-06-12

### Added
- Added `ignorecase` support.
- Added debug support.
- Added support for including site directories.

### Changed
- Improved compatibility and CI behavior.

## [v0.8.2] - 2025-04-14

### Fixed
- Fixed documentation issues.

## [v0.8.1] - 2025-03-29

### Fixed
- Hardened replacement behavior.
- Added alternate path separator handling.
- Fixed path-related issues.

## [v0.8.0] - 2025-03-29

### Changed
- Removed pylint exclusions from the project configuration.

## [v0.7.0] - 2025-03-23

### Fixed
- Fixed a cache issue on Windows.

## [v0.6.0] - 2024-10-29

### Changed
- Switched to dynamic versioning.

## [v0.5.0] - 2024-08-27

### Added
- Added flavour support to `assert_refdata`.

## [0.4.2] - 2024-01-24

### Changed
- Version bump release.

## [0.4.1] - 2024-01-24

### Changed
- Version bump release.

## [0.4.0] - 2024-01-22

### Changed
- Version bump release.

## [0.3.0] - 2024-01-18

### Changed
- Version bump release.

## [0.2.0] - 2024-01-16

### Changed
- Version bump release.

## [0.1.0] - 2024-01-16

### Changed
- Initial release.
- Dropped Python 3.7 support.
