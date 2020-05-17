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

from datetime import datetime
import json
from os.path import isfile, join, splitext
from os import listdir, remove
from time import time

from octobot_backtesting.data import DataBaseNotExists
from octobot_backtesting.data.database import DataBase
from octobot_commons.enums import TimeFrames

from octobot_backtesting.constants import BACKTESTING_DATA_FILE_TIME_DISPLAY_FORMAT, BACKTESTING_DATA_FILE_EXT, \
    BACKTESTING_DATA_FILE_SEPARATOR
from octobot_backtesting.enums import DataFormatKeys, DataFormats, DataTables


def get_backtesting_file_name(clazz, data_format=DataFormats.REGULAR_COLLECTOR_DATA):
    return f"{clazz.__name__}{BACKTESTING_DATA_FILE_SEPARATOR}" \
           f"{time()}{get_file_ending(data_format)}"


def get_data_type(file_name):
    if file_name.endswith(BACKTESTING_DATA_FILE_EXT):
        return DataFormats.REGULAR_COLLECTOR_DATA


def get_file_ending(data_type):
    if data_type == DataFormats.REGULAR_COLLECTOR_DATA:
        return BACKTESTING_DATA_FILE_EXT


def get_date(time_info) -> str:
    """
    :param time_info: Timestamp in seconds of the time to convert
    :return: A human readable date at the backtesting data file time format
    """
    return datetime.fromtimestamp(time_info).strftime(BACKTESTING_DATA_FILE_TIME_DISPLAY_FORMAT)


async def get_database_description(database):
    description = (await database.select(DataTables.DESCRIPTION, size=1))[0]
    version = description[1]
    if version == "1.0":
        return {
            DataFormatKeys.DATE.value: description[0],
            DataFormatKeys.VERSION.value: description[1],
            DataFormatKeys.EXCHANGE.value: description[2],
            DataFormatKeys.SYMBOLS.value: json.loads(description[3]),
            DataFormatKeys.TIME_FRAMES.value: [TimeFrames(tf) for tf in json.loads(description[4])]
        }
    else:
        raise RuntimeError(f"Unknown datafile version: {version}")


async def get_file_description(database_file):
    database = None
    try:
        database = DataBase(database_file)
        await database.initialize()
        description = await get_database_description(database)
    except (DataBaseNotExists, TypeError):
        description = None
    finally:
        if database is not None:
            await database.stop()
    return description


def is_valid_ending(ending):
    return ending in [BACKTESTING_DATA_FILE_EXT]


def get_all_available_data_files(data_collector_path):
    try:
        files = [file
                 for file in listdir(data_collector_path)
                 if isfile(join(data_collector_path, file)) and is_valid_ending(splitext(file)[1])]
    except FileNotFoundError:
        files = []
    return files


def delete_data_file(data_collector_path, file_name):
    try:
        file_path = join(data_collector_path, file_name)
        if isfile(file_path):
            remove(file_path)
            return True, ""
        else:
            return False, f"file can't be found"
    except Exception as e:
        return False, e
