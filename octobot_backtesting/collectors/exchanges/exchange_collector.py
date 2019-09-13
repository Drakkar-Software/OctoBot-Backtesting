#  Drakkar-Software OctoBot
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
import logging
import time

from octobot_commons.constants import CONFIG_TIME_FRAME

from octobot_backtesting.collectors.data_collector import DataCollector
from octobot_backtesting.constants import BACKTESTING_DATA_FILE_EXT

try:
    from octobot_trading.constants import CONFIG_EXCHANGES, CONFIG_CRYPTO_CURRENCIES, CONFIG_CRYPTO_PAIRS
except ImportError:
    logging.error("ExchangeDataCollector requires OctoBot-Trading package installed")


class ExchangeDataCollector(DataCollector):
    def __init__(self, config, exchange_name, symbols, time_frames):
        super().__init__(config)
        self.exchange_name = exchange_name
        self.symbols = symbols if symbols else []
        self.time_frames = time_frames if time_frames else []
        self.file_name = f"{exchange_name}_{time.time()}{BACKTESTING_DATA_FILE_EXT}"
        self.set_file_path()

    async def initialize(self):
        self.create_database()

        # set config from params
        self.config[CONFIG_TIME_FRAME] = self.time_frames
        self.config[CONFIG_EXCHANGES] = {self.exchange_name: {}}
        self.config[CONFIG_CRYPTO_CURRENCIES] = {"Symbols": {CONFIG_CRYPTO_PAIRS: self.symbols}}
