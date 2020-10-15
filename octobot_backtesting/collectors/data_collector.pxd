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

cimport octobot_backtesting.data as data

cdef class DataCollector:
    cdef public dict config

    cdef public object logger
    cdef public object aiohttp_session

    cdef public bint should_stop

    cdef public str file_name
    cdef public str file_path
    cdef public str path

    cdef public data.DataBase database

    cpdef void create_database(self)
    cpdef void create_aiohttp_session(self)
    cpdef void set_file_path(self)

    cdef void _ensure_file_path(self)
