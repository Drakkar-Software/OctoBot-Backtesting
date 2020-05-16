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
from octobot_backtesting.api.importer import get_data_timestamp_interval
from octobot_backtesting.data import MissingTimeFrame
from octobot_commons.constants import CONFIG_ENABLED_OPTION, MINUTE_TO_SECONDS
from octobot_backtesting.backtesting import Backtesting
from octobot_backtesting.constants import CONFIG_BACKTESTING, CONFIG_BACKTESTING_DATA_FILES
from octobot_commons.enums import TimeFramesMinutes
from octobot_commons.logging.logging_util import get_logger
from octobot_commons.time_frame_manager import find_min_time_frame, get_config_time_frame


async def initialize_backtesting(config, exchange_ids, matrix_id, data_files) -> Backtesting:
    backtesting_instance = Backtesting(config=config,
                                       exchange_ids=exchange_ids,
                                       matrix_id=matrix_id,
                                       backtesting_files=data_files)
    await backtesting_instance.create_importers()
    await backtesting_instance.initialize()

    if not backtesting_instance.importers:
        raise ValueError("No importers created")

    return backtesting_instance


async def initialize_independent_backtesting_config(independent_backtesting) -> dict:
    return await independent_backtesting.initialize_config()


async def modify_backtesting_timestamps(backtesting, set_timestamp=None,
                                        minimum_timestamp=None, maximum_timestamp=None) -> None:
    await backtesting.time_updater.modify(set_timestamp=set_timestamp,
                                          minimum_timestamp=minimum_timestamp,
                                          maximum_timestamp=maximum_timestamp)


async def adapt_backtesting_channels(backtesting, config, importer_class, run_on_common_part_only=True):
    # set mininmum and maximum timestamp according to all importers data
    min_time_frame_to_consider = find_min_time_frame(get_config_time_frame(config))
    importers = backtesting.get_importers(importer_class)
    try:
        timestamps = [await get_data_timestamp_interval(importer, min_time_frame_to_consider)
                      for importer in importers]  # [(min, max) ... ]
    except MissingTimeFrame as e:
        raise RuntimeError(f"Impossible to start backtesting on this configuration: {e}")
    min_timestamps = [timestamp[0] for timestamp in timestamps]
    max_timestamps = [timestamp[1] for timestamp in timestamps]

    min_timestamp = max(min_timestamps) if run_on_common_part_only else min(min_timestamps)
    max_timestamps = min(max_timestamps) if run_on_common_part_only else max(max_timestamps)

    if min_timestamp > max_timestamps:
        raise RuntimeError(f"No candle data to run backtesting on in this time window: starting at: {min_timestamp} "
                           f"and ending at: {max_timestamps}")

    await modify_backtesting_timestamps(
        backtesting,
        minimum_timestamp=min_timestamp,
        maximum_timestamp=max_timestamps)
    try:
        from octobot_trading.api.exchange import has_only_ohlcv

        if has_only_ohlcv(importers):
            set_time_updater_interval(backtesting,
                                      TimeFramesMinutes[min_time_frame_to_consider] * MINUTE_TO_SECONDS)
    except ImportError:
        get_logger("BacktestingAPI").error("requires OctoBot-Trading package installed")


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
    return CONFIG_BACKTESTING in config and CONFIG_ENABLED_OPTION in config[CONFIG_BACKTESTING] \
           and config[CONFIG_BACKTESTING][CONFIG_ENABLED_OPTION]


def get_backtesting_data_files(config) -> list:
    if CONFIG_BACKTESTING in config and CONFIG_BACKTESTING_DATA_FILES in config[CONFIG_BACKTESTING]:
        return config[CONFIG_BACKTESTING][CONFIG_BACKTESTING_DATA_FILES]
    return []


def get_backtesting_duration(backtesting) -> float:
    return backtesting.time_updater.simulation_duration
