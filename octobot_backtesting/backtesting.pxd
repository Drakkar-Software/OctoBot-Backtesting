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

cdef class Backtesting:
    cdef public object config

    cdef public list backtesting_files
    cdef public list importers

    cdef public TimeManager time_manager

    cdef object logger

    cpdef list get_importers(self, object importer_parent_class=*)
    cpdef float get_progress(self)
    cpdef bool is_in_progress(self)

    cdef bool _has_nothing_to_do(self)
