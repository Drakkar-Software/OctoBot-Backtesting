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

cdef class TimeManager:
    cdef object logger

    cdef dict config
    
    cdef public float starting_timestamp
    cdef public float finishing_timestamp
    cdef public float current_timestamp

    cdef public bint time_initialized

    cdef void __reset_time(self)

    cpdef void initialize(self)
    cpdef void start(self)
    cpdef bint has_finished(self)
    cpdef void next_timestamp(self)
    cpdef void set_minimum_timestamp(self, float minimum_timestamp)
    cpdef void set_maximum_timestamp(self, float maximum_timestamp)
    cpdef void set_current_timestamp(self, float timestamp)
    cpdef float get_total_iteration(self)
    cpdef float get_remaining_iteration(self)
