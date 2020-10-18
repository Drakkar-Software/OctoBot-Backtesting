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
import os
import typing

import octobot_backtesting.constants as constants
import octobot_backtesting.collectors as collectors
import octobot_backtesting.importers as importers
import octobot_commons.tentacles_management as tentacles_management


async def create_importer_from_backtesting_file_name(config,
                                                     backtesting_file) -> typing.Optional[importers.DataImporter]:
    collector_klass = tentacles_management.get_deep_class_from_parent_subclasses(
        _parse_class_name_from_backtesting_file(backtesting_file), collectors.DataCollector)
    importer = collector_klass.IMPORTER(config, backtesting_file) if collector_klass else None

    if not importer:
        return None

    await importer.initialize()
    return importer


def _parse_class_name_from_backtesting_file(backtesting_file):
    return os.path.basename(backtesting_file).split(constants.BACKTESTING_DATA_FILE_SEPARATOR)[0]
