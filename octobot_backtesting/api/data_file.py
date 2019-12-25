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
from octobot_backtesting.constants import BACKTESTING_FILE_PATH
from octobot_backtesting.data import data_file_manager as data_manager


def get_file_description(file_name, data_path=BACKTESTING_FILE_PATH):
    return data_manager.get_file_description(data_path, file_name)


def get_all_available_data_files(data_path=BACKTESTING_FILE_PATH):
    return data_manager.get_all_available_data_files(data_path)


def delete_data_file(file_name, data_path=BACKTESTING_FILE_PATH):
    return data_manager.delete_data_file(data_path, file_name)
