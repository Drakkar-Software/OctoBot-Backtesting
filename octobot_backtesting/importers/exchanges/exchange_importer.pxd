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
cimport octobot_backtesting.importers as importers

cdef class ExchangeDataImporter(importers.DataImporter):
    cdef public str exchange_name

    cdef public list available_data_types
    cdef public list symbols
    cdef public list time_frames

    cdef tuple __get_operations_from_timestamps(self, double superior_timestamp, double inferior_timestamp)
    cdef list import_ohlcvs(self, list ohlcvs)
    cdef list import_tickers(self, list tickers)
    cdef list import_klines(self, list klines)
    cdef list import_order_books(self, list order_books)
    cdef list import_recent_trades(self, list recent_trades)
