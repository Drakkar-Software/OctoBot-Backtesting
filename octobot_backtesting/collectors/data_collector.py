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
import time
from os.path import join

from octobot_commons.logging.logging_util import get_logger

from octobot_backtesting.constants import BACKTESTING_DATA_FILE_EXT, BACKTESTING_FILE_PATH, \
    BACKTESTING_DATA_FILE_SEPARATOR
from octobot_backtesting.data.database import DataBase
from octobot_backtesting.importers.data_importer import DataImporter


class DataCollector:
    IMPORTER = DataImporter

    def __init__(self, config, path=BACKTESTING_FILE_PATH):
        self.config = config
        self.path = path
        self.logger = get_logger(self.__class__.__name__)

        self.should_stop = False
        self.file_name = f"{self.__class__.__name__}{BACKTESTING_DATA_FILE_SEPARATOR}" \
                         f"{time.time()}{BACKTESTING_DATA_FILE_EXT}"

        self.database = None
        self.file_path = None
        self.set_file_path()

    async def initialize(self) -> None:
        pass

    async def stop(self) -> None:
        self.should_stop = True

    async def start(self) -> None:
        raise NotImplementedError("Start is not implemented")

    def set_file_path(self) -> None:
        self.file_path = join(self.path, self.file_name) if self.path else self.file_name

    def create_database(self) -> None:
        if not self.database:
            self.database = DataBase(self.file_path)
