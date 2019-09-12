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

from octobot_commons.logging.logging_util import get_logger

from octobot_backtesting.data.database import DataBase


class DataCollector:
    def __init__(self, config, exchange_name, symbols, time_frames):
        self.config = config
        self.exchange_name = exchange_name
        self.symbols = symbols if symbols else []
        self.time_frames = time_frames if time_frames else []
        self.logger = get_logger(self.__class__.__name__)

        self.should_stop = False
        self.file_name = f"{exchange_name}_{time.time()}"
        self.database = DataBase(self.file_name)

    async def initialize(self):
        pass

    async def stop(self) -> None:
        self.should_stop = True

    async def start(self) -> None:
        raise NotImplementedError("Start is not implemented")
