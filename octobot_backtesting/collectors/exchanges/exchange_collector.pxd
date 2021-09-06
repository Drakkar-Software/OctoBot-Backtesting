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

cimport octobot_backtesting.collectors.data_collector as data_collector


cdef class ExchangeDataCollector(data_collector.DataCollector):
    cdef public str exchange_name

    cdef public list symbols
    cdef public list time_frames
    cdef public object tentacles_setup_config
    cdef public object start_timestamp
    cdef public object end_timestamp
    cdef public int current_time_frame_index
    cdef public int total_time_frame
    cdef public float current_time_frame_percent

    cdef bint use_all_available_timeframes

    cpdef int get_current_time_frame_index(self)
    cpdef int get_total_time_frame(self)
    cpdef float get_current_time_frame_percent(self)

    cpdef void _load_timeframes_if_necessary(self)
    cpdef void _load_all_available_timeframes(self)
