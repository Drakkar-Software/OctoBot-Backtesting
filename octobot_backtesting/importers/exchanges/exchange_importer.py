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
import octobot_commons.constants as common_constants
import octobot_commons.enums as common_enums
import octobot_commons.errors as common_errors
import octobot_commons.databases as databases

import octobot_backtesting.data as data
import octobot_backtesting.enums as enums
import octobot_backtesting.errors as errors
import octobot_backtesting.importers.data_importer as data_importer
import octobot_backtesting.importers.exchanges.util as util


class ExchangeDataImporter(data_importer.DataImporter):
    def __init__(self, config, file_path):
        super().__init__(config, file_path)

        self.exchange_name = None
        self.symbols = []
        self.time_frames = []
        self.available_data_types = []

        # TODO remove when new symbol format is supported
        self.legacy_symbol_to_storage_symbol = {}

    async def initialize(self) -> None:
        self.load_database()
        await self.database.initialize()

        # load description
        description = await data.get_database_description(self.database)
        self.exchange_name = description[enums.DataFormatKeys.EXCHANGE.value]
        self.symbols = description[enums.DataFormatKeys.SYMBOLS.value]
        self.legacy_symbol_to_storage_symbol = self.get_legacy_symbol_dict(self.symbols)
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
                    min_timestamp = (await self.database.select_min(table,
                                                                    [databases.SQLiteDatabase.TIMESTAMP_COLUMN]))[0][0]
                    if not minimum_timestamp or minimum_timestamp > min_timestamp:
                        minimum_timestamp = min_timestamp

                    max_timestamp = (await self.database.select_max(table,
                                                                    [databases.SQLiteDatabase.TIMESTAMP_COLUMN]))[0][0]
                    if not maximum_timestamp or maximum_timestamp < max_timestamp:
                        maximum_timestamp = max_timestamp
                except (IndexError, common_errors.DatabaseNotFoundError):
                    pass

        # OHLCV timestamps
        try:
            ohlcv_kwargs = {"time_frame": time_frame} if time_frame else {}
            ohlcv_min_timestamps = (await self.database.select_min(enums.ExchangeDataTables.OHLCV,
                                                                   [databases.SQLiteDatabase.TIMESTAMP_COLUMN],
                                                                   [common_constants.CONFIG_TIME_FRAME],
                                                                   group_by=common_constants.CONFIG_TIME_FRAME,
                                                                   **ohlcv_kwargs
                                                                   ))

            if ohlcv_min_timestamps:
                # if the required time frame is not included in this database, ohlcv_min_timestamps is empty: ignore it
                min_ohlcv_timestamp = max(ohlcv_min_timestamps)[0]
                max_ohlcv_timestamp = (await self.database.select_max(enums.ExchangeDataTables.OHLCV,
                                                                      [databases.SQLiteDatabase.TIMESTAMP_COLUMN],
                                                                      **ohlcv_kwargs))[0][0]
            elif time_frame:
                raise errors.MissingTimeFrame(f"Missing time frame in data file: {time_frame}")

        except (IndexError, common_errors.DatabaseNotFoundError):
            pass

        if minimum_timestamp > 0 and maximum_timestamp > 0:
            return max(minimum_timestamp, min_ohlcv_timestamp), max(maximum_timestamp, max_ohlcv_timestamp)
        return min_ohlcv_timestamp, max_ohlcv_timestamp

    async def _init_available_data_types(self):
        self.available_data_types = [table for table in enums.ExchangeDataTables
                                     if await self.database.check_table_exists(table)
                                     and await self.database.check_table_not_empty(table)]

    async def _get_from_db(
            self, exchange_name, symbol, table,
            time_frame=None,
            limit=databases.SQLiteDatabase.DEFAULT_SIZE,
            timestamps=None,
            operations=None
    ):
        symbol = self._get_importer_symbol(symbol)
        kwargs = {} if time_frame is None else {"time_frame": time_frame.value}

        if timestamps:
            return await self.database.select_from_timestamp(
                table, size=limit,
                exchange_name=exchange_name, symbol=symbol,
                timestamps=timestamps,
                operations=operations,
                **kwargs
            )
        return await self.database.select(
            table, size=limit,
            exchange_name=exchange_name, symbol=symbol,
            **kwargs
        )

    async def get_ohlcv(self, exchange_name=None, symbol=None,
                        time_frame=common_enums.TimeFrames.ONE_HOUR,
                        limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                        timestamps=None,
                        operations=None):
        return util.import_ohlcvs(await self._get_from_db(
            exchange_name, symbol, enums.ExchangeDataTables.OHLCV,
            time_frame=time_frame,
            limit=limit,
            timestamps=timestamps,
            operations=operations
        ))

    async def get_ohlcv_from_timestamps(self, exchange_name=None, symbol=None,
                                        time_frame=common_enums.TimeFrames.ONE_HOUR,
                                        limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                                        inferior_timestamp=-1, superior_timestamp=-1) -> list:
        """
        Reads OHLCV history from database and populates a local ChronologicalReadDatabaseCache.
        Warning: can't read data from before last given inferior_timestamp unless associated cache is reset
        """
        return await self._get_from_cache(exchange_name, symbol, time_frame, enums.ExchangeDataTables.OHLCV,
                                          inferior_timestamp, superior_timestamp, self.get_ohlcv, limit)

    async def get_ticker(self, exchange_name=None, symbol=None,
                         limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                         timestamps=None,
                         operations=None):
        return util.import_tickers(await self._get_from_db(
            exchange_name, symbol, enums.ExchangeDataTables.TICKER,
            limit=limit,
            timestamps=timestamps,
            operations=operations
        ))

    async def get_ticker_from_timestamps(self, exchange_name=None, symbol=None,
                                         limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                                         inferior_timestamp=-1, superior_timestamp=-1):
        """
        Reads ticker history from database and populates a local ChronologicalReadDatabaseCache.
        Warning: can't read data from before last given inferior_timestamp unless associated cache is reset
        """
        return await self._get_from_cache(exchange_name, symbol, None, enums.ExchangeDataTables.TICKER,
                                          inferior_timestamp, superior_timestamp, self.get_ticker, limit)

    async def get_order_book(self, exchange_name=None, symbol=None,
                             limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                             timestamps=None,
                             operations=None):
        return util.import_order_books(await self._get_from_db(
            exchange_name, symbol, enums.ExchangeDataTables.ORDER_BOOK,
            limit=limit,
            timestamps=timestamps,
            operations=operations
        ))

    async def get_order_book_from_timestamps(self, exchange_name=None, symbol=None,
                                             limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                                             inferior_timestamp=-1, superior_timestamp=-1):
        """
        Reads order book history from database and populates a local ChronologicalReadDatabaseCache.
        Warning: can't read data from before last given inferior_timestamp unless associated cache is reset
        """
        return await self._get_from_cache(exchange_name, symbol, None, enums.ExchangeDataTables.ORDER_BOOK,
                                          inferior_timestamp, superior_timestamp, self.get_order_book, limit)

    async def get_recent_trades(self, exchange_name=None, symbol=None,
                                limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                                timestamps=None,
                                operations=None):
        return util.import_recent_trades(await self._get_from_db(
            exchange_name, symbol, enums.ExchangeDataTables.RECENT_TRADES,
            limit=limit,
            timestamps=timestamps,
            operations=operations
        ))

    async def get_recent_trades_from_timestamps(self, exchange_name=None, symbol=None,
                                                limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                                                inferior_timestamp=-1, superior_timestamp=-1):
        """
        Reads recent trades history from database and populates a local ChronologicalReadDatabaseCache.
        Warning: can't read data from before last given inferior_timestamp unless associated cache is reset
        """
        return await self._get_from_cache(exchange_name, symbol, None, enums.ExchangeDataTables.RECENT_TRADES,
                                          inferior_timestamp, superior_timestamp, self.get_recent_trades, limit)

    async def get_kline(self, exchange_name=None, symbol=None,
                        time_frame=common_enums.TimeFrames.ONE_HOUR,
                        limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                        timestamps=None,
                        operations=None):
        return util.import_klines(await self._get_from_db(
            exchange_name, symbol, enums.ExchangeDataTables.KLINE,
            time_frame=time_frame,
            limit=limit,
            timestamps=timestamps,
            operations=operations
        ))

    async def get_kline_from_timestamps(self, exchange_name=None, symbol=None,
                                        time_frame=common_enums.TimeFrames.ONE_HOUR,
                                        limit=databases.SQLiteDatabase.DEFAULT_SIZE,
                                        inferior_timestamp=-1, superior_timestamp=-1):
        """
        Reads kline history from database and populates a local ChronologicalReadDatabaseCache.
        Warning: can't read data from before last given inferior_timestamp unless associated cache is reset
        """
        return await self._get_from_cache(exchange_name, symbol, time_frame, enums.ExchangeDataTables.KLINE,
                                          inferior_timestamp, superior_timestamp, self.get_kline, limit)

    async def _get_from_cache(self, exchange_name, symbol, time_frame, data_type,
                              inferior_timestamp, superior_timestamp, set_cache_method, limit):
        symbol = self._get_importer_symbol(symbol)
        if not self.chronological_cache.has((exchange_name, symbol, time_frame, data_type)):
            # ignore superior timestamp to select everything starting from inferior_timestamp and cache it
            select_superior_timestamp = -1
            timestamps, operations = util.get_operations_from_timestamps(
                select_superior_timestamp,
                inferior_timestamp
            )
            # initializer without time_frame args are not expecting the time_frame argument, remove it
            # ignore the limit param as it might reduce the available cache and give false later select results
            init_cache_method_args = \
                (exchange_name, symbol, databases.SQLiteDatabase.DEFAULT_SIZE, timestamps, operations) \
                if time_frame is None \
                else (exchange_name, symbol, time_frame, databases.SQLiteDatabase.DEFAULT_SIZE, timestamps, operations)
            self.chronological_cache.set(
                await set_cache_method(*init_cache_method_args),
                0,
                (exchange_name, symbol, time_frame, data_type)
            )
        return self.chronological_cache.get(inferior_timestamp, superior_timestamp,
                                            (exchange_name, symbol, time_frame, data_type))

    def _get_importer_symbol(self, symbol):
        # TODO remove when full symbol handling
        try:
            return symbol if symbol in self.symbols else self.legacy_symbol_to_storage_symbol[symbol]
        except KeyError:
            return symbol

    @staticmethod
    def get_legacy_symbol_dict(symbols):
        return {
            symbol.split(":")[0]: symbol
            for symbol in symbols
        }
