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
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.


cdef class OctoBotBacktesting:
    cdef public dict backtesting_config
    cdef public object tentacles_setup_config

    cdef object logger

    cdef public str matrix_id
    cdef public list exchange_manager_ids
    cdef public dict symbols_to_create_exchange_classes
    cdef public list evaluators
    cdef public dict fees_config
    cdef public list backtesting_files
    cdef public list backtestings

    cpdef void memory_leak_checkup(self, list to_check_elements)
    cpdef void check_remaining_objects(self)

    cdef void _log_remaining_object_error(self, object obj, int expected, int actual)
    cdef void _register_backtesting(self, object exchange_manager)
    cdef void _log_import_error(self)
