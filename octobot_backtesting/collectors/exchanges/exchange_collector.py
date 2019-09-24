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
import json
import logging
import time

from octobot_commons.constants import CONFIG_TIME_FRAME

from octobot_backtesting.collectors.data_collector import DataCollector
from octobot_backtesting.enums import ExchangeDataTables, DataTables
from octobot_backtesting.importers.exchanges.exchange_importer import ExchangeDataImporter

try:
    from octobot_trading.constants import CONFIG_EXCHANGES, CONFIG_CRYPTO_CURRENCIES, CONFIG_CRYPTO_PAIRS
except ImportError:
    logging.error("ExchangeDataCollector requires OctoBot-Trading package installed")


class ExchangeDataCollector(DataCollector):
    VERSION = "1.0"
    IMPORTER = ExchangeDataImporter

    def __init__(self, config, exchange_name, symbols, time_frames):
        super().__init__(config)
        self.exchange_name = exchange_name
        self.symbols = symbols if symbols else []
        self.time_frames = time_frames if time_frames else []
        self.set_file_path()

    async def initialize(self):
        self.create_database()
        await self.database.initialize()

        # set config from params
        self.config[CONFIG_TIME_FRAME] = self.time_frames
        self.config[CONFIG_EXCHANGES] = {self.exchange_name: {}}
        self.config[CONFIG_CRYPTO_CURRENCIES] = {"Symbols": {CONFIG_CRYPTO_PAIRS: self.symbols}}

        # create description
        await self.database.insert(DataTables.DESCRIPTION,
                                   timestamp=time.time(),
                                   version=self.VERSION,
                                   exchange=self.exchange_name,
                                   symbols=json.dumps(self.symbols),
                                   time_frames=json.dumps([tf.value for tf in self.time_frames]))

    async def save_ticker(self, timestamp, exchange, symbol, ticker):
        await self.database.insert(ExchangeDataTables.TICKER, timestamp, exchange_name=exchange, symbol=symbol,
                                   ticker=json.dumps(ticker))

    async def save_order_book(self, timestamp, exchange, symbol, asks, bids):
        await self.database.insert(ExchangeDataTables.ORDER_BOOK, timestamp,
                                   exchange_name=exchange, symbol=symbol, asks=asks, bids=bids)

    async def save_recent_trades(self, timestamp, exchange, symbol, recent_trades):
        await self.database.insert(ExchangeDataTables.RECENT_TRADES, timestamp,
                                   exchange_name=exchange, symbol=symbol, recent_trades=json.dumps(recent_trades))

    async def save_ohlcv(self, timestamp, exchange, symbol, time_frame, candle, multiple=False):
        if not multiple:
            await self.database.insert(ExchangeDataTables.OHLCV, timestamp,
                                       exchange_name=exchange, symbol=symbol, time_frame=time_frame.value,
                                       candle=candle)
        else:
            await self.database.insert_all(ExchangeDataTables.OHLCV, timestamp=timestamp,
                                           exchange_name=exchange, symbol=symbol, time_frame=time_frame.value,
                                           candle=candle)

    async def save_kline(self, timestamp, exchange, symbol, time_frame, kline):
        await self.database.insert(ExchangeDataTables.KLINE, timestamp,
                                   exchange_name=exchange, symbol=symbol, time_frame=time_frame.value, kline=kline)
