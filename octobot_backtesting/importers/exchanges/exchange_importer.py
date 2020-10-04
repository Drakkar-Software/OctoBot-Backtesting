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

import octobot_commons.constants as common_constants
import octobot_commons.enums as common_enums

import octobot_backtesting.data as data
import octobot_backtesting.enums as enums
import octobot_backtesting.errors as errors
import octobot_backtesting.importers as importers


class ExchangeDataImporter(importers.DataImporter):
    def __init__(self, config, file_path):
        super().__init__(config, file_path)

        self.exchange_name = None
        self.symbols = []
        self.time_frames = []
        self.available_data_types = []

    async def initialize(self) -> None:
        self.load_database()
        await self.database.initialize()

        # load description
        description = await data.get_database_description(self.database)
        self.exchange_name = description[enums.DataFormatKeys.EXCHANGE.value]
        self.symbols = description[enums.DataFormatKeys.SYMBOLS.value]
        self.time_frames = description[enums.DataFormatKeys.TIME_FRAMES.value]
        await self._init_available_data_types()

        self.logger.info(f"Loaded {self.exchange_name} data file with "
                         f"{', '.join(self.symbols)} on {', '.join([tf.value for tf in self.time_frames])}")

    async def start(self) -> None:
        pass

    async def get_data_timestamp_interval(self, time_frame=None):
        minimum_timestamp: float = 0.0
        maximum_timestamp: float = 0.0

        min_ohlcv_timestamp: float = 0.0
        max_ohlcv_timestamp: float = 0.0

        for table in [enums.ExchangeDataTables.KLINE, enums.ExchangeDataTables.ORDER_BOOK,
                      enums.ExchangeDataTables.RECENT_TRADES, enums.ExchangeDataTables.TICKER]:
            if table in self.available_data_types:
                try:
                    min_timestamp = (await self.database.select_min(table, [data.DataBase.TIMESTAMP_COLUMN]))[0][0]
                    if not minimum_timestamp or minimum_timestamp > min_timestamp:
                        minimum_timestamp = min_timestamp

                    max_timestamp = (await self.database.select_max(table, [data.DataBase.TIMESTAMP_COLUMN]))[0][0]
                    if not maximum_timestamp or maximum_timestamp < max_timestamp:
                        maximum_timestamp = max_timestamp
                except (IndexError, errors.DataBaseNotExists):
                    pass

        # OHLCV timestamps
        try:
            ohlcv_kwargs = {"time_frame": time_frame} if time_frame else {}
            ohlcv_min_timestamps = (await self.database.select_min(enums.ExchangeDataTables.OHLCV,
                                                                   [data.DataBase.TIMESTAMP_COLUMN],
                                                                   [common_constants.CONFIG_TIME_FRAME],
                                                                   group_by=common_constants.CONFIG_TIME_FRAME,
                                                                   **ohlcv_kwargs
                                                                   ))

            if ohlcv_min_timestamps:
                # if the required time frame is not included in this database, ohlcv_min_timestamps is empty: ignore it
                min_ohlcv_timestamp = max(ohlcv_min_timestamps)[0]
                max_ohlcv_timestamp = (await self.database.select_max(enums.ExchangeDataTables.OHLCV,
                                                                      [data.DataBase.TIMESTAMP_COLUMN],
                                                                      **ohlcv_kwargs))[0][0]
            elif time_frame:
                raise errors.MissingTimeFrame(f"Missing time frame in data file: {time_frame}")

        except (IndexError, errors.DataBaseNotExists):
            pass

        if minimum_timestamp > 0 and maximum_timestamp > 0:
            return max(minimum_timestamp, min_ohlcv_timestamp), max(maximum_timestamp, max_ohlcv_timestamp)
        return min_ohlcv_timestamp, max_ohlcv_timestamp

    async def _init_available_data_types(self):
        self.available_data_types = [table for table in enums.ExchangeDataTables
                                     if await self.database.check_table_exists(table)
                                     and await self.database.check_table_not_empty(table)]

    def __get_operations_from_timestamps(self, superior_timestamp, inferior_timestamp):
        operations: list = []
        timestamps: list = []
        if superior_timestamp != -1:
            timestamps.append(str(superior_timestamp))
            operations.append(enums.DataBaseOperations.INF_EQUALS.value)
        if inferior_timestamp != -1:
            timestamps.append(str(inferior_timestamp))
            operations.append(enums.DataBaseOperations.SUP_EQUALS.value)

        return timestamps, operations

    def import_ohlcvs(self, ohlcvs):
        for i, val in enumerate(ohlcvs):
            ohlcvs[i] = list(val)
            # ohlcvs[i][-2] = TimeFrames(ohlcvs[i][-2])
            ohlcvs[i][-1] = json.loads(ohlcvs[i][-1])
        return ohlcvs

    async def get_ohlcv(self, exchange_name=None, symbol=None,
                        time_frame=common_enums.TimeFrames.ONE_HOUR,
                        limit=data.DataBase.DEFAULT_SIZE):
        return self.import_ohlcvs(await self.database.select(enums.ExchangeDataTables.OHLCV, size=limit,
                                                             exchange_name=exchange_name, symbol=symbol,
                                                             time_frame=time_frame.value))

    async def get_ohlcv_from_timestamps(self, exchange_name=None, symbol=None,
                                        time_frame=common_enums.TimeFrames.ONE_HOUR,
                                        limit=data.DataBase.DEFAULT_SIZE,
                                        inferior_timestamp=-1, superior_timestamp=-1) -> list:
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_ohlcvs(await self.database.select_from_timestamp(enums.ExchangeDataTables.OHLCV, size=limit,
                                                                            exchange_name=exchange_name, symbol=symbol,
                                                                            time_frame=time_frame.value,
                                                                            timestamps=timestamps,
                                                                            operations=operations))

    def import_tickers(self, tickers):
        for ticker in tickers:
            ticker[-1] = json.loads(ticker[-1])
        return tickers

    async def get_ticker(self, exchange_name=None, symbol=None, limit=data.DataBase.DEFAULT_SIZE):
        return self.import_tickers(await self.database.select(enums.ExchangeDataTables.TICKER, size=limit,
                                                              exchange_name=exchange_name, symbol=symbol))

    async def get_ticker_from_timestamps(self, exchange_name=None, symbol=None, limit=data.DataBase.DEFAULT_SIZE,
                                         inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_tickers(await self.database.select_from_timestamp(enums.ExchangeDataTables.TICKER, size=limit,
                                                                             exchange_name=exchange_name, symbol=symbol,
                                                                             timestamps=timestamps,
                                                                             operations=operations))

    def import_order_books(self, order_books):
        for order_book in order_books:
            order_book[-1] = json.loads(order_book[-1])
            order_book[-2] = json.loads(order_book[-2])
        return order_books

    async def get_order_book(self, exchange_name=None, symbol=None, limit=data.DataBase.DEFAULT_SIZE):
        return self.import_order_books(await self.database.select(enums.ExchangeDataTables.ORDER_BOOK, size=limit,
                                                                  exchange_name=exchange_name, symbol=symbol))

    async def get_order_book_from_timestamps(self, exchange_name=None, symbol=None, limit=data.DataBase.DEFAULT_SIZE,
                                             inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_order_books(
            await self.database.select_from_timestamp(enums.ExchangeDataTables.ORDER_BOOK, size=limit,
                                                      exchange_name=exchange_name, symbol=symbol,
                                                      timestamps=timestamps, operations=operations))

    def import_recent_trades(self, recent_trades):
        for recent_trade in recent_trades:
            recent_trade[-1] = json.loads(recent_trade[-1])
        return recent_trades

    async def get_recent_trades(self, exchange_name=None, symbol=None, limit=data.DataBase.DEFAULT_SIZE):
        return self.import_recent_trades(await self.database.select(enums.ExchangeDataTables.RECENT_TRADES, size=limit,
                                                                    exchange_name=exchange_name, symbol=symbol))

    async def get_recent_trades_from_timestamps(self, exchange_name=None, symbol=None, limit=data.DataBase.DEFAULT_SIZE,
                                                inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_recent_trades(await
                                         self.database.select_from_timestamp(enums.ExchangeDataTables.RECENT_TRADES,
                                                                             size=limit,
                                                                             exchange_name=exchange_name,
                                                                             symbol=symbol,
                                                                             timestamps=timestamps,
                                                                             operations=operations))

    def import_klines(self, klines):
        for kline in klines:
            kline[-1] = json.loads(kline[-1])
        return klines

    async def get_kline(self, exchange_name=None, symbol=None,
                        time_frame=common_enums.TimeFrames.ONE_HOUR, limit=data.DataBase.DEFAULT_SIZE):
        return self.import_klines(await self.database.select(enums.ExchangeDataTables.KLINE, size=limit,
                                                             exchange_name=exchange_name, symbol=symbol,
                                                             time_frame=time_frame.value))

    async def get_kline_from_timestamps(self, exchange_name=None, symbol=None,
                                        time_frame=common_enums.TimeFrames.ONE_HOUR,
                                        limit=data.DataBase.DEFAULT_SIZE,
                                        inferior_timestamp=-1, superior_timestamp=-1):
        timestamps, operations = self.__get_operations_from_timestamps(superior_timestamp, inferior_timestamp)
        return self.import_klines(await self.database.select_from_timestamp(enums.ExchangeDataTables.KLINE, size=limit,
                                                                            exchange_name=exchange_name, symbol=symbol,
                                                                            time_frame=time_frame.value,
                                                                            timestamps=timestamps,
                                                                            operations=operations))
