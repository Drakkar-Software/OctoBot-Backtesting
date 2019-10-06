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
import json

from octobot_commons.enums import TimeFrames

from octobot_backtesting.data import DataBaseNotExists
from octobot_backtesting.data.database import DataBase
from octobot_backtesting.enums import ExchangeDataTables, DataBaseOperations, DataBaseOrderBy, DataTables
from octobot_backtesting.importers.data_importer import DataImporter


class ExchangeDataImporter(DataImporter):
    def __init__(self, config, file_path):
        super().__init__(config, file_path)

        self.exchange_name = None
        self.symbols = []
        self.time_frames = []

    async def initialize(self) -> None:
        self.load_database()
        await self.database.initialize()

        # load description
        description = (await self.database.select(DataTables.DESCRIPTION, size=1))[0]

        version = description[1]
        if version == "1.0":
            self.exchange_name = description[2]
            self.symbols = json.loads(description[3])
            self.time_frames = [TimeFrames(tf) for tf in json.loads(description[4])]

        self.logger.info(f"Loaded {self.exchange_name} data file with "
                         f"{', '.join(self.symbols)} on {', '.join([tf.value for tf in self.time_frames])}")

    async def start(self) -> None:
        pass

    async def get_data_timestamp_interval(self):
        minimum_timestamp: float = 0.0
        maximum_timestamp: float = 0.0
        for table in ExchangeDataTables:
            try:
                min_timestamp = (await self.database.select(table, size=1, sort=DataBaseOrderBy.ASC.value))[0][0]
                if not minimum_timestamp or minimum_timestamp > min_timestamp:
                    minimum_timestamp = min_timestamp

                max_timestamp = (await self.database.select(table, size=1, sort=DataBaseOrderBy.DESC.value))[0][0]
                if not maximum_timestamp or maximum_timestamp > max_timestamp:
                    maximum_timestamp = max_timestamp
            except (IndexError, DataBaseNotExists):
                pass
        return minimum_timestamp, maximum_timestamp

    def __get_operations_from_timestamps(self, superior_timestamp, inferior_timestamp):
        operations: list = []
        timestamps: list = []
        if superior_timestamp != -1:
            timestamps.append(str(superior_timestamp))
            operations.append(DataBaseOperations.SUP_EQUALS.value)
        if inferior_timestamp != -1:
            timestamps.append(str(inferior_timestamp))
            operations.append(DataBaseOperations.INF_EQUALS.value)

        return timestamps, operations

    def import_ohlcvs(self, ohlcvs):
        for i in range(len(ohlcvs)):
            ohlcvs[i] = list(ohlcvs[i])
            # ohlcvs[i][-2] = TimeFrames(ohlcvs[i][-2])
            ohlcvs[i][-1] = json.loads(ohlcvs[i][-1])
        return ohlcvs

    async def get_ohlcv(self, exchange_name=None, symbol=None, time_frame=None, limit=DataBase.DEFAULT_SIZE):
        return self.import_ohlcvs(await self.database.select(ExchangeDataTables.OHLCV, size=limit,
                                                             exchange_name=exchange_name, symbol=symbol,
                                                             time_frame=time_frame.value))

    async def get_ohlcv_from_timestamps(self, exchange_name=None, symbol=None, time_frame=None,
                                        limit=DataBase.DEFAULT_SIZE,
                                        inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_ohlcvs(await self.database.select_from_timestamp(ExchangeDataTables.OHLCV, size=limit,
                                                                            exchange_name=exchange_name, symbol=symbol,
                                                                            time_frame=time_frame.value,
                                                                            timestamps=timestamps,
                                                                            operations=operations))

    def import_tickers(self, tickers):
        for ticker in tickers:
            ticker[-1] = json.loads(ticker[-1])
        return tickers

    async def get_ticker(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return self.import_tickers(await self.database.select(ExchangeDataTables.TICKER, size=limit,
                                                              exchange_name=exchange_name, symbol=symbol))

    async def get_ticker_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                         inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_tickers(await self.database.select_from_timestamp(ExchangeDataTables.TICKER, size=limit,
                                                                             exchange_name=exchange_name, symbol=symbol,
                                                                             timestamps=timestamps,
                                                                             operations=operations))

    def import_order_books(self, order_books):
        for order_book in order_books:
            order_book[-1] = json.loads(order_book[-1])
            order_book[-2] = json.loads(order_book[-2])
        return order_books

    async def get_order_book(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return self.import_order_books(await self.database.select(ExchangeDataTables.ORDER_BOOK, size=limit,
                                                                  exchange_name=exchange_name, symbol=symbol))

    async def get_order_book_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                             inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_order_books(
            await self.database.select_from_timestamp(ExchangeDataTables.ORDER_BOOK, size=limit,
                                                      exchange_name=exchange_name, symbol=symbol,
                                                      timestamps=timestamps, operations=operations))

    def import_recent_trades(self, recent_trades):
        for recent_trade in recent_trades:
            recent_trade[-1] = json.loads(recent_trade[-1])
        return recent_trades

    async def get_recent_trades(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return self.import_recent_trades(await self.database.select(ExchangeDataTables.RECENT_TRADES, size=limit,
                                                                    exchange_name=exchange_name, symbol=symbol))

    async def get_recent_trades_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                                inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_recent_trades(await
                                         self.database.select_from_timestamp(ExchangeDataTables.RECENT_TRADES,
                                                                             size=limit,
                                                                             exchange_name=exchange_name,
                                                                             symbol=symbol,
                                                                             timestamps=timestamps,
                                                                             operations=operations))

    def import_klines(self, klines):
        for kline in klines:
            kline[-1] = json.loads(kline[-1])
        return klines

    async def get_kline(self, exchange_name=None, symbol=None, time_frame=None, limit=DataBase.DEFAULT_SIZE):
        return self.import_klines(await self.database.select(ExchangeDataTables.KLINE, size=limit,
                                                             exchange_name=exchange_name, symbol=symbol,
                                                             time_frame=time_frame.value))

    async def get_kline_from_timestamps(self, exchange_name=None, symbol=None, time_frame=None,
                                        limit=DataBase.DEFAULT_SIZE,
                                        inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_klines(await self.database.select_from_timestamp(ExchangeDataTables.KLINE, size=limit,
                                                                            exchange_name=exchange_name, symbol=symbol,
                                                                            time_frame=time_frame.value,
                                                                            timestamps=timestamps,
                                                                            operations=operations))
