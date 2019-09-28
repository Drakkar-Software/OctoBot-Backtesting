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
            self.time_frames = json.loads(description[4])

        self.logger.info(f"Loaded {self.exchange_name} data file with "
                         f"{', '.join(self.symbols)} on {', '.join(self.time_frames)}")

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
            except IndexError:
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

    async def get_ohlcv(self, exchange_name=None, symbol=None, time_frame=None, limit=DataBase.DEFAULT_SIZE):
        return await self.database.select(ExchangeDataTables.OHLCV, size=limit,
                                          exchange_name=exchange_name, symbol=symbol, time_frame=time_frame)

    async def get_ohlcv_from_timestamps(self, exchange_name=None, symbol=None, time_frame=None,
                                        limit=DataBase.DEFAULT_SIZE,
                                        inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return await self.database.select_from_timestamp(ExchangeDataTables.OHLCV, size=limit,
                                                         exchange_name=exchange_name, symbol=symbol,
                                                         time_frame=time_frame,
                                                         timestamps=timestamps, operations=operations)

    async def get_ticker(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return await self.database.select(ExchangeDataTables.TICKER, size=limit,
                                          exchange_name=exchange_name, symbol=symbol)

    async def get_ticker_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                         inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return await self.database.select_from_timestamp(ExchangeDataTables.TICKER, size=limit,
                                                         exchange_name=exchange_name, symbol=symbol,
                                                         timestamps=timestamps, operations=operations)

    async def get_order_book(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return await self.database.select(ExchangeDataTables.ORDER_BOOK, size=limit,
                                          exchange_name=exchange_name, symbol=symbol)

    async def get_order_book_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                             inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return await self.database.select_from_timestamp(ExchangeDataTables.ORDER_BOOK, size=limit,
                                                         exchange_name=exchange_name, symbol=symbol,
                                                         timestamps=timestamps, operations=operations)

    async def get_recent_trades(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return await self.database.select(ExchangeDataTables.RECENT_TRADES, size=limit,
                                          exchange_name=exchange_name, symbol=symbol)

    async def get_recent_trades_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                                inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return await self.database.select_from_timestamp(ExchangeDataTables.RECENT_TRADES, size=limit,
                                                         exchange_name=exchange_name, symbol=symbol,
                                                         timestamps=timestamps, operations=operations)

    async def get_kline(self, exchange_name=None, symbol=None, time_frame=None, limit=DataBase.DEFAULT_SIZE):
        return await self.database.select(ExchangeDataTables.KLINE, size=limit,
                                          exchange_name=exchange_name, symbol=symbol, time_frame=time_frame)

    async def get_kline_from_timestamps(self, exchange_name=None, symbol=None, time_frame=None,
                                        limit=DataBase.DEFAULT_SIZE,
                                        inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return await self.database.select_from_timestamp(ExchangeDataTables.KLINE, size=limit,
                                                         exchange_name=exchange_name, symbol=symbol,
                                                         time_frame=time_frame,
                                                         timestamps=timestamps, operations=operations)
