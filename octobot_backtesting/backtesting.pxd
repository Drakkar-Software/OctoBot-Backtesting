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
from octobot_backtesting.data_manager.time_manager cimport TimeManager
from octobot_backtesting.channels.time cimport TimeChannel

cdef class Backtesting:
    cdef public object config

    cdef public list backtesting_files
    cdef public list importers
    cdef public list exchange_ids

    cdef public str matrix_id

    cdef public TimeManager time_manager
    cdef public object time_updater
    cdef public TimeChannel time_channel
    cdef object logger

    cpdef list get_importers(self, object importer_parent_class=*)
    cpdef double get_progress(self)
    cpdef bint is_in_progress(self)

    cdef bint _has_nothing_to_do(self)
