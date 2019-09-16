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
from octobot_commons.logging.logging_util import get_logger

from octobot_backtesting.data.database import DataBase


class DataImporter:
    def __init__(self, config, file_path):
        self.config = config
        self.file_path = file_path
        self.logger = get_logger(self.__class__.__name__)

        self.should_stop = False

        self.database = None

    async def initialize(self) -> None:
        pass

    def get_data_timestamp_interval(self) -> float:
        raise NotImplementedError("get_data_timestamp_interval is not implemented")

    async def stop(self) -> None:
        self.should_stop = True

    async def start(self) -> None:
        raise NotImplementedError("Start is not implemented")

    def load_database(self) -> None:
        if not self.database:
            self.database = DataBase(self.file_path)
