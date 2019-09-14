# cython: language_level=3
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
#  Lesser General License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
from octobot_backtesting.importers.data_importer cimport DataImporter

cdef class ExchangeDataImporter(DataImporter):
    cdef tuple __get_operations_from_timestamps(self, float superior_timestamp, float inferior_timestamp)

    cpdef list get_ohlcv(self, exchange_name=*, symbol=*, time_frame=*, limit=*)

    cpdef list get_ohlcv_from_timestamps(self, exchange_name=*, symbol=*, time_frame=*, limit=*,
                                  inferior_timestamp=*, superior_timestamp=*)

    cpdef list get_ticker(self, exchange_name=*, symbol=*, limit=*)

    cpdef list get_ticker_from_timestamps(self, exchange_name=*, symbol=*, limit=*,
                                  inferior_timestamp=*, superior_timestamp=*)

    cpdef list get_order_book(self, exchange_name=*, symbol=*, limit=*)

    cpdef list get_order_book_from_timestamps(self, exchange_name=*, symbol=*, limit=*,
                                  inferior_timestamp=*, superior_timestamp=*)

    cpdef list get_recent_trades(self, exchange_name=*, symbol=*, limit=*)

    cpdef list get_recent_trades_from_timestamps(self, exchange_name=*, symbol=*, limit=*,
                                  inferior_timestamp=*, superior_timestamp=*)

    cpdef list get_kline(self, exchange_name=*, symbol=*, time_frame=*, limit=*)

    cpdef list get_kline_from_timestamps(self, exchange_name=*, symbol=*, time_frame=*, limit=*,
                                  inferior_timestamp=*, superior_timestamp=*)
