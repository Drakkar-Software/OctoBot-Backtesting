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
import asyncio
import json
import logging
import time

from octobot_commons.channels_name import OctoBotTradingChannelsName
from octobot_commons.constants import CONFIG_TIME_FRAME

from octobot_backtesting.collectors.data_collector import DataCollector
from octobot_backtesting.enums import DataBaseTables

try:
    from octobot_trading.channels.exchange_channel import get_chan
    from octobot_trading.api.exchange import create_new_exchange
    from octobot_trading.constants import CONFIG_EXCHANGES, CONFIG_CRYPTO_CURRENCIES, CONFIG_CRYPTO_PAIRS
except ImportError:
    logging.error("ExchangeDataCollector requires OctoBot-Trading package installed")


class ExchangeDataCollector(DataCollector):
    async def initialize(self):
        # set config from params
        self.config[CONFIG_TIME_FRAME] = self.time_frames
        self.config[CONFIG_EXCHANGES] = {self.exchange_name: {}}
        self.config[CONFIG_CRYPTO_CURRENCIES] = {"Symbols": {CONFIG_CRYPTO_PAIRS: self.symbols}}

    async def start(self):
        exchange_factory = create_new_exchange(self.config, self.exchange_name, is_simulated=True, is_rest_only=True,
                                               is_collecting=True)
        await exchange_factory.create_basic()

        await get_chan(OctoBotTradingChannelsName.TICKER_CHANNEL.value,
                       self.exchange_name).new_consumer(self.ticker_callback)
        await get_chan(OctoBotTradingChannelsName.RECENT_TRADES_CHANNEL.value,
                       self.exchange_name).new_consumer(self.recent_trades_callback)
        await get_chan(OctoBotTradingChannelsName.ORDER_BOOK_CHANNEL.value,
                       self.exchange_name).new_consumer(self.order_book_callback)
        await get_chan(OctoBotTradingChannelsName.KLINE_CHANNEL.value,
                       self.exchange_name).new_consumer(self.kline_callback)
        await get_chan(OctoBotTradingChannelsName.OHLCV_CHANNEL.value,
                       self.exchange_name).new_consumer(self.ohlcv_callback)

        await asyncio.gather(*asyncio.all_tasks(asyncio.get_event_loop()))

    async def ticker_callback(self, exchange, symbol, ticker):
        self.logger.info(f"TICKER : SYMBOL = {symbol} || TICKER = {ticker}")
        self.database.insert(DataBaseTables.TICKER, time.time(), symbol=symbol, ticker=ticker)

    async def order_book_callback(self, exchange, symbol, asks, bids):
        self.logger.info(f"ORDERBOOK : SYMBOL = {symbol} || ASKS = {asks} || BIDS = {bids}")
        self.database.insert(DataBaseTables.ORDER_BOOK, time.time(), symbol=symbol, asks=asks, bids=bids)

    async def ohlcv_callback(self, exchange, symbol, time_frame, candle):
        self.logger.info(f"OHLCV : SYMBOL = {symbol} || TIME FRAME = {time_frame} || CANDLE = {candle}")
        self.database.insert(DataBaseTables.OHLCV, time.time(), symbol=symbol, time_frame=time_frame.value, candle=candle)

    async def recent_trades_callback(self, exchange, symbol, recent_trades):
        self.logger.info(f"RECENT TRADE : SYMBOL = {symbol} || RECENT TRADE = {recent_trades}")
        self.database.insert(DataBaseTables.RECENT_TRADES, time.time(), symbol=symbol, recent_trades=json.dumps(recent_trades))

    async def kline_callback(self, exchange, symbol, time_frame, kline):
        self.logger.info(f"KLINE : SYMBOL = {symbol} || TIME FRAME = {time_frame} || KLINE = {kline}")
        self.database.insert(DataBaseTables.KLINE, time.time(), symbol=symbol, time_frame=time_frame.value, kline=kline)
