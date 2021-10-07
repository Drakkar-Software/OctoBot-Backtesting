#  Drakkar-Software OctoBot-Backtesting
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import octobot_commons.constants as common_constants
import octobot_commons.enums as common_enums
import octobot_commons.logging as logging
import octobot_commons.time_frame_manager as time_frame_manager

import octobot_backtesting.api as api
import octobot_backtesting.errors as errors
import octobot_backtesting.backtesting as backtesting_class
import octobot_backtesting.constants as constants


async def initialize_backtesting(config, exchange_ids, matrix_id, data_files) -> backtesting_class.Backtesting:
    backtesting_instance = backtesting_class.Backtesting(config=config,
                                                         exchange_ids=exchange_ids,
                                                         matrix_id=matrix_id,
                                                         backtesting_files=data_files)
    await backtesting_instance.create_importers()
    await backtesting_instance.initialize()

    if not backtesting_instance.importers:
        raise ValueError("No importers created: did you enter the backtesting file(s) to use ?")

    return backtesting_instance


async def initialize_independent_backtesting_config(independent_backtesting) -> dict:
    return await independent_backtesting.initialize_config()


async def modify_backtesting_timestamps(backtesting, set_timestamp=None,
                                        minimum_timestamp=None, maximum_timestamp=None) -> None:
    await backtesting.time_updater.modify(set_timestamp=set_timestamp,
                                          minimum_timestamp=minimum_timestamp,
                                          maximum_timestamp=maximum_timestamp)


async def adapt_backtesting_channels(backtesting, config, importer_class, run_on_common_part_only=True,
                                     start_timestamp=None, end_timestamp=None):
    # set mininmum and maximum timestamp according to all importers data
    min_time_frame_to_consider = time_frame_manager.find_min_time_frame(
        time_frame_manager.get_config_time_frame(config))
    importers = backtesting.get_importers(importer_class)
    if not importers:
        raise RuntimeError("No exchange importer has been found for this data file, backtesting can't start.")
    try:
        timestamps = [await api.get_data_timestamp_interval(importer, min_time_frame_to_consider)
                      for importer in importers]  # [(min, max) ... ]
    except errors.MissingTimeFrame as e:
        raise RuntimeError(f"Impossible to start backtesting on this configuration: {e}")
    min_timestamps = [timestamp[0] for timestamp in timestamps]
    max_timestamps = [timestamp[1] for timestamp in timestamps]

    min_timestamp = max(min_timestamps) if run_on_common_part_only else min(min_timestamps)
    max_timestamp = min(max_timestamps) if run_on_common_part_only else max(max_timestamps)

    if min_timestamp > max_timestamp:
        raise RuntimeError(f"No candle data to run backtesting on in this time window: starting at: {min_timestamp} "
                           f"and ending at: {max_timestamp}")
    if start_timestamp is not None and end_timestamp is not None and \
            start_timestamp > end_timestamp:
        raise RuntimeError(f"No candle data to run backtesting on in this time window: starting at: {start_timestamp} "
                           f"and ending at: {end_timestamp}")

    if start_timestamp is not None:
        if min_timestamp <= start_timestamp < end_timestamp if end_timestamp else max_timestamp:
            min_timestamp = start_timestamp
        else:
            logging.get_logger("BacktestingAPI").warning(f"Can't set the minimum timestamp to {start_timestamp}. "
                                                         f"The minimum available({min_timestamp}) will be used instead.")
    if end_timestamp is not None:
        if max_timestamp >= end_timestamp > start_timestamp if start_timestamp else min_timestamp:
            max_timestamp = end_timestamp
        else:
            logging.get_logger("BacktestingAPI").warning(f"Can't set the maximum timestamp to {end_timestamp}. "
                                                         f"The maximum available({max_timestamp}) will be used instead.")

    await modify_backtesting_timestamps(
        backtesting,
        minimum_timestamp=min_timestamp,
        maximum_timestamp=max_timestamp)
    try:
        import octobot_trading.api as exchange_api

        if exchange_api.has_only_ohlcv(importers):
            set_time_updater_interval(backtesting,
                                      common_enums.TimeFramesMinutes[min_time_frame_to_consider] *
                                      common_constants.MINUTE_TO_SECONDS)
    except ImportError:
        logging.get_logger("BacktestingAPI").error("requires OctoBot-Trading package installed")


def set_time_updater_interval(backtesting, interval_in_seconds):
    backtesting.time_manager.time_interval = interval_in_seconds


async def start_backtesting(backtesting) -> None:
    await backtesting.start_time_updater()


async def stop_backtesting(backtesting) -> None:
    await backtesting.stop()


async def stop_independent_backtesting(independent_backtesting) -> None:
    await independent_backtesting.stop()


def get_importers(backtesting) -> list:
    return backtesting.importers


def get_backtesting_current_time(backtesting) -> float:
    return backtesting.time_manager.current_timestamp


def is_backtesting_enabled(config) -> bool:
    return constants.CONFIG_BACKTESTING in config \
           and common_constants.CONFIG_ENABLED_OPTION in config[constants.CONFIG_BACKTESTING] \
           and config[constants.CONFIG_BACKTESTING][common_constants.CONFIG_ENABLED_OPTION]


def get_backtesting_data_files(config) -> list:
    return config.get(constants.CONFIG_BACKTESTING, {}).get(constants.CONFIG_BACKTESTING_DATA_FILES, [])


def get_backtesting_duration(backtesting) -> float:
    return backtesting.time_updater.simulation_duration
