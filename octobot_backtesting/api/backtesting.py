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
from octobot_commons.constants import CONFIG_ENABLED_OPTION

from octobot_backtesting.backtesting import Backtesting
from octobot_backtesting.constants import CONFIG_BACKTESTING, CONFIG_BACKTESTING_DATA_FILES


def create_backtesting(config, data_files) -> Backtesting:
    return Backtesting(config, data_files)


async def initialize_created_backtesting(backtesting_instance) -> Backtesting:
    await backtesting_instance.create_importers()
    await backtesting_instance.initialize()

    if not backtesting_instance.importers:
        raise ValueError("No importers created")

    return backtesting_instance


async def initialize_backtesting(config, data_files) -> Backtesting:
    backtesting_instance = Backtesting(config, data_files)
    await backtesting_instance.create_importers()
    await backtesting_instance.initialize()

    if not backtesting_instance.importers:
        raise ValueError("No importers created")

    return backtesting_instance


async def modify_backtesting_timestamps(backtesting, set_timestamp=None,
                                        minimum_timestamp=None, maximum_timestamp=None) -> None:
    await backtesting.time_updater.modify(set_timestamp=set_timestamp,
                                          minimum_timestamp=minimum_timestamp,
                                          maximum_timestamp=maximum_timestamp)


def set_time_updater_interval(backtesting, interval_in_seconds):
    backtesting.time_manager.time_interval = interval_in_seconds


async def start_backtesting(backtesting) -> None:
    await backtesting.start_time_updater()


def is_backtesting_in_progress(backtesting) -> bool:
    return backtesting.is_in_progress()


def get_backtesting_current_time(backtesting) -> float:
    return backtesting.time_manager.current_timestamp


def get_backtesting_progress(backtesting) -> float:
    return backtesting.get_progress()


def get_backtesting_run_report(backtesting) -> dict:
    # TODO: add backtesting report handling
    # return backtesting.get_report()
    return {}


def is_backtesting_enabled(config) -> bool:
    return CONFIG_BACKTESTING in config and CONFIG_ENABLED_OPTION in config[CONFIG_BACKTESTING] \
           and config[CONFIG_BACKTESTING][CONFIG_ENABLED_OPTION]


def get_backtesting_data_files(config) -> list:
    if CONFIG_BACKTESTING in config and CONFIG_BACKTESTING_DATA_FILES in config[CONFIG_BACKTESTING]:
        return config[CONFIG_BACKTESTING][CONFIG_BACKTESTING_DATA_FILES]
    return []
