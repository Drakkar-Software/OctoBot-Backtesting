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

from octobot_commons.constants import CONFIG_TIME_FRAME

from octobot_backtesting.collectors.data_collector import DataCollector
from octobot_backtesting.enums import ExchangeDataTables
from octobot_backtesting.importers.exchanges.exchange_importer import ExchangeDataImporter

try:
    from octobot_trading.constants import CONFIG_EXCHANGES, CONFIG_CRYPTO_CURRENCIES, CONFIG_CRYPTO_PAIRS
except ImportError:
    logging.error("ExchangeDataCollector requires OctoBot-Trading package installed")


class ExchangeDataCollector(DataCollector):
    IMPORTER = ExchangeDataImporter

    def __init__(self, config, exchange_name, symbols, time_frames):
        super().__init__(config)
        self.exchange_name = exchange_name
        self.symbols = symbols if symbols else []
        self.time_frames = time_frames if time_frames else []
        self.set_file_path()

    async def initialize(self):
        self.create_database()

        # set config from params
        self.config[CONFIG_TIME_FRAME] = self.time_frames
        self.config[CONFIG_EXCHANGES] = {self.exchange_name: {}}
        self.config[CONFIG_CRYPTO_CURRENCIES] = {"Symbols": {CONFIG_CRYPTO_PAIRS: self.symbols}}

    def save_ticker(self, timestamp, exchange, symbol, ticker):
        self.database.insert(ExchangeDataTables.TICKER, timestamp, exchange_name=exchange, symbol=symbol, ticker=ticker)

    def save_order_book(self, timestamp, exchange, symbol, asks, bids):
        self.database.insert(ExchangeDataTables.ORDER_BOOK, timestamp,
                             exchange_name=exchange, symbol=symbol, asks=asks, bids=bids)

    def save_recent_trades(self, timestamp, exchange, symbol, recent_trades):
        self.database.insert(ExchangeDataTables.RECENT_TRADES, timestamp,
                             exchange_name=exchange, symbol=symbol, recent_trades=json.dumps(recent_trades))

    def save_ohlcv(self, timestamp, exchange, symbol, time_frame, candle, multiple=False):
        if not multiple:
            self.database.insert(ExchangeDataTables.OHLCV, timestamp,
                                 exchange_name=exchange, symbol=symbol, time_frame=time_frame.value, candle=candle)
        else:
            self.database.insert_all(ExchangeDataTables.OHLCV, timestamp=timestamp,
                                     exchange_name=exchange, symbol=symbol, time_frame=time_frame.value, candle=candle)

    def save_kline(self, timestamp, exchange, symbol, time_frame, kline):
        self.database.insert(ExchangeDataTables.KLINE, timestamp,
                             exchange_name=exchange, symbol=symbol, time_frame=time_frame.value, kline=kline)
