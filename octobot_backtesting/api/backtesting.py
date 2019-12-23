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
from octobot_backtesting.constants import CONFIG_BACKTESTING


async def initialize_backtesting(config, data_files) -> Backtesting:
    backtesting_instance = Backtesting(config, data_files)
    await backtesting_instance.initialize()
    await backtesting_instance.create_importers()

    if not backtesting_instance.importers:
        raise ValueError("No importers created")

    return backtesting_instance


def is_backtesting_enabled(config):
    return CONFIG_BACKTESTING in config and CONFIG_ENABLED_OPTION in config[CONFIG_BACKTESTING] \
           and config[CONFIG_BACKTESTING][CONFIG_ENABLED_OPTION]
