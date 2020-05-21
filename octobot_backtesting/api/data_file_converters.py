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
from os.path import isfile

from octobot_backtesting.converters.data_converter import DataConverter
from octobot_commons.tentacles_management.class_inspector import get_all_classes_from_parent


async def convert_data_file(data_file_path) -> str:
    if data_file_path and isfile(data_file_path):
        converter_classes = get_all_classes_from_parent(DataConverter)
        for converter_class in converter_classes:
            converter = converter_class(data_file_path)
            if await converter.can_convert():
                if await converter.convert():
                    return converter.converted_file
    return None
