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

from octobot_backtesting.collectors.data_collector cimport DataCollector


cdef class ExchangeDataCollector(DataCollector):
    cdef public str exchange_name

    cdef public list symbols
    cdef public list time_frames

    cpdef void save_ticker(self, object timestamp, str exchange, str symbol, object ticker)
    cpdef void save_order_book(self, object timestamp, str exchange, str symbol, object asks, object bids)
    cpdef void save_recent_trades(self, object timestamp, str exchange, str symbol, object recent_trades)
    cpdef void save_ohlcv(self, object timestamp, str exchange, str symbol, object time_frame, object candle, bint multiple=*)
    cpdef void save_kline(self, object timestamp, str exchange, str symbol, object time_frame, object kline)
