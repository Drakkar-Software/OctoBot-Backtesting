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
from octobot_backtesting.data.database import DataBase
from octobot_backtesting.enums import DataBaseTables, DataBaseOperations
from octobot_backtesting.importers.data_importer import DataImporter


class ExchangeDataImporter(DataImporter):
    def initialize(self) -> None:
        self.load_database()

    async def start(self) -> None:
        pass

    def __get_operations_from_timestamps(self, superior_timestamp, inferior_timestamp):
        operations = []
        timestamps = []
        if superior_timestamp is not None:
            timestamps.append(superior_timestamp)
            operations.append(DataBaseOperations.SUP_EQUALS.value)
        if inferior_timestamp is not None:
            timestamps.append(inferior_timestamp)
            operations.append(DataBaseOperations.INF_EQUALS.value)

        return timestamps, operations

    def get_ohlcv(self, exchange_name=None, symbol=None, time_frame=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.OHLCV, size=limit,
                                    exchange_name=exchange_name, symbol=symbol, time_frame=time_frame)

    def get_ohlcv_from_timestamps(self, exchange_name=None, symbol=None, time_frame=None, limit=DataBase.DEFAULT_SIZE,
                                  inferior_timestamp=None, superior_timestamp=None):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.database.select_from_timestamp(DataBaseTables.OHLCV, size=limit,
                                                   exchange_name=exchange_name, symbol=symbol,
                                                   time_frame=time_frame,
                                                   timestamps=timestamps, operations=operations)

    def get_ticker(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.TICKER, size=limit,
                                    exchange_name=exchange_name, symbol=symbol,)

    def get_ticker_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                  inferior_timestamp=None, superior_timestamp=None):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.database.select_from_timestamp(DataBaseTables.TICKER, size=limit,
                                                   exchange_name=exchange_name, symbol=symbol,
                                                   timestamps=timestamps, operations=operations)

    def get_order_book(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.ORDER_BOOK, size=limit,
                                    exchange_name=exchange_name, symbol=symbol)

    def get_order_book_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                  inferior_timestamp=None, superior_timestamp=None):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.database.select_from_timestamp(DataBaseTables.ORDER_BOOK, size=limit,
                                                   exchange_name=exchange_name, symbol=symbol,
                                                   timestamps=timestamps, operations=operations)

    def get_recent_trades(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.RECENT_TRADES, size=limit,
                                    exchange_name=exchange_name, symbol=symbol)

    def get_recent_trades_from_timestamps(self, exchange_name=None, symbol=None, limit=DataBase.DEFAULT_SIZE,
                                  inferior_timestamp=None, superior_timestamp=None):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.database.select_from_timestamp(DataBaseTables.RECENT_TRADES, size=limit,
                                                   exchange_name=exchange_name, symbol=symbol,
                                                   timestamps=timestamps, operations=operations)

    def get_kline(self, exchange_name=None, symbol=None, time_frame=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.KLINE, size=limit,
                                    exchange_name=exchange_name, symbol=symbol, time_frame=time_frame)

    def get_kline_from_timestamps(self, exchange_name=None, symbol=None, time_frame=None, limit=DataBase.DEFAULT_SIZE,
                                  inferior_timestamp=None, superior_timestamp=None):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.database.select_from_timestamp(DataBaseTables.KLINE, size=limit,
                                                   exchange_name=exchange_name, symbol=symbol,
                                                   time_frame=time_frame,
                                                   timestamps=timestamps, operations=operations)
