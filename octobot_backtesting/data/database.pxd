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

cdef class DataBase:
    cdef str file_name

    cdef object logger
    cdef object connection
    cdef object cursor

    cdef list tables

    cdef void stop(self)

    cdef void __insert_values(self, object table, int timestamp, str inserting_values)
    cdef bint __check_table_exists(self, object table)
    cdef str __select_order_by(self, str order_by, str sort)
    cdef str __where_clauses_from_operations(self, list keys, list values, list operations)
    cdef str __where_clauses_from_operation(self, str key, str value, str operation=*)
    cdef void __init_tables_list(self)
