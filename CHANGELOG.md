# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.9] - 2020-02-17
### Added
- Backtesting finished event

### Updated
- Data converters
- Backtesting API
- DataFile converter API
- Database error handling
- IndependentBacktesting flexibily for strategy optimizer

### Fixed
- Compiled double accuracy

## [1.3.8] - 2020-02-06
### Added
- Independent backtesting handling

### Updated
- Backtesting API
- Importer API
- DataFile API

## [1.3.7] - 2020-02-02
### Updated
- Backtesting API
- Importer API

## [1.3.6] - 2020-01-26
### Updated
- Backtesting API
- Backtesting workflow

## [1.3.5] - 2020-01-23
### Updated
- Backtesting API

## [1.3.4] - 2020-01-18
### Added
- AbstractExchangeHistoryCollector and AbstractExchangeLiveCollector

### Updated
- Data collector to work from web interface
- collect_exchange_historical_data and get_file_description APIs

## [1.3.3] - 2020-01-02
### Added
- Backtesting, data_file and exchange_data_collector API
- is_in_progress method in Backtesting
- use_all_available_timeframes in exchange collector

### Updated
- data_file_manager imports
- Commons version to 1.2.1

## [1.3.2] - 2019-12-21
### Updated
**Requirements**
- Commons version to 1.2.0
- Channels version to 1.3.6

## [1.3.1] - 2019-12-14
### Updated
**Requirements**
- Commons version to 1.1.51
- Channels version to 1.3.6
- aiosqlite version to 0.11.0

## [1.3.0] - 2019-11-07
## Added
- Timestamp interval management (starting and stopping)

### Fixed
- Database select where clauses generation

## [1.2.5] - 2019-10-30
## Added
- OSX support

## [1.2.4] - 2019-10-09
## Added
- PyPi manylinux deployment

## [1.2.3] - 2019-10-08
### Changed
- Constants VERSION and PROJECT_NAME file location 

## [1.2.2] - 2019-10-08
## Fixed
- Install with setup

## [1.2.1] - 2019-10-07
### Added
- Collector async http with aiohttp

### Changed
- Improved database management

## [1.2.0] - 2019-10-05
### Added
- Converters classes
- Database indexes
- Tentacles management (Importers, Collectors, Converters)
- Database async management

### Changed
- Fully async backtesting

## [1.1.1] - 2019-09-18
### Added
- Time management from OctoBot-Trading

## [1.1.0] - 2019-09-16
### Added
- Collectors basis
- Importers basis
- Exchange collectors (Live and History)
- Exchange importer
- Database manager

## [1.0.0] - 2019-09-10
### Added
- Package components from OctoBot project
