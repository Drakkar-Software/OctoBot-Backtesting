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
from octobot_backtesting.enums import DataBaseTables
from octobot_backtesting.importers.data_importer import DataImporter


class ExchangeDataImporter(DataImporter):
    def __init__(self, config, file_path):
        super().__init__(config, file_path)

    def initialize(self) -> None:
        self.load_database()

    async def start(self) -> None:
        pass

    def get_ohlcv(self, exchange_name=None, symbol=None, time_frame=None, timestamp=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.OHLCV, size=limit,
                                    exchange_name=exchange_name, symbol=symbol, time_frame=time_frame,
                                    timestamp=timestamp)

    def get_ticker(self, exchange_name=None, symbol=None, timestamp=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.TICKER, size=limit,
                                    exchange_name=exchange_name, symbol=symbol, timestamp=timestamp)

    def get_order_book(self, exchange_name=None, symbol=None, timestamp=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.ORDER_BOOK, size=limit,
                                    exchange_name=exchange_name, symbol=symbol, timestamp=timestamp)

    def get_recent_trades(self, exchange_name=None, symbol=None, timestamp=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.RECENT_TRADES, size=limit,
                                    exchange_name=exchange_name, symbol=symbol, timestamp=timestamp)

    def get_kline(self, exchange_name=None, symbol=None, time_frame=None, timestamp=None, limit=DataBase.DEFAULT_SIZE):
        return self.database.select(DataBaseTables.KLINE, size=limit,
                                    exchange_name=exchange_name, symbol=symbol, time_frame=time_frame,
                                    timestamp=timestamp)
