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


def is_backtesting_in_progress(backtesting):
    return backtesting.is_in_progress()


def get_backtesting_current_time(backtesting):
    return backtesting.time_manager.current_timestamp


def get_backtesting_progress(backtesting):
    return backtesting.get_progress()


def get_backtesting_run_report(backtesting):
    # TODO: add backtesting report handling
    # return backtesting.get_report()
    return {}


def is_backtesting_enabled(config):
    return CONFIG_BACKTESTING in config and CONFIG_ENABLED_OPTION in config[CONFIG_BACKTESTING] \
           and config[CONFIG_BACKTESTING][CONFIG_ENABLED_OPTION]


def get_backtesting_data_files(config):
    if CONFIG_BACKTESTING in config and CONFIG_BACKTESTING_DATA_FILES in config[CONFIG_BACKTESTING]:
        return config[CONFIG_BACKTESTING][CONFIG_BACKTESTING_DATA_FILES]
    return []
