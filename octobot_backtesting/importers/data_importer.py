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
from octobot_backtesting.data import BacktestingFileNotFound
from octobot_commons.logging.logging_util import get_logger

from octobot_backtesting.data.database import DataBase


class DataImporter:
    def __init__(self, config, file_path):
        self.config = config
        self.file_path = file_path
        self.logger = get_logger(self.__class__.__name__)

        self.should_stop = False

        self.version = None
        self.database = None

    async def initialize(self) -> None:
        pass

    async def get_data_timestamp_interval(self, time_frame=None):
        raise NotImplementedError("get_data_timestamp_interval is not implemented")

    async def stop(self) -> None:
        if not self.should_stop:
            self.should_stop = True
            await self.database.stop()

    async def start(self) -> None:
        raise NotImplementedError("Start is not implemented")

    def load_database(self) -> None:
        file_path = self.adapt_file_path_if_necessary()
        if not self.database:
            self.database = DataBase(file_path)

    def adapt_file_path_if_necessary(self):
        if path.isfile(self.file_path):
            return self.file_path
        else:
            candidate_path = path.join(BACKTESTING_FILE_PATH, self.file_path)
            if path.isfile(candidate_path):
                return candidate_path
        raise BacktestingFileNotFound(f"File {self.file_path} not found")
