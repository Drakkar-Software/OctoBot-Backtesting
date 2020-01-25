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
from os import path
from octobot_backtesting.constants import BACKTESTING_FILE_PATH
from octobot_backtesting.data import data_file_manager as data_manager, DataBaseNotExists
from octobot_backtesting.data.database import DataBase


async def get_file_description(file_name, data_path=BACKTESTING_FILE_PATH) -> dict:
    database = None
    try:
        database = DataBase(path.join(data_path, file_name))
        await database.initialize()
        description = await data_manager.get_file_description(database)
    except DataBaseNotExists as e:
        print(e)
        description = None
    except TypeError as e:
        print(e)
        description = None
    finally:
        if database is not None:
            await database.stop()
    return description


def get_all_available_data_files(data_path=BACKTESTING_FILE_PATH) -> list:
    return data_manager.get_all_available_data_files(data_path)


def delete_data_file(file_name, data_path=BACKTESTING_FILE_PATH) -> tuple:
    return data_manager.delete_data_file(data_path, file_name)
