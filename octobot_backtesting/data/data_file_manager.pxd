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

cpdef object get_data_type(str file_name)
cpdef str get_file_ending(object data_type)
cpdef str get_date(int time_info)
cpdef bint is_valid_ending(str ending)
cpdef list get_all_available_data_files(str data_collector_path)
cpdef object delete_data_file(str data_collector_path, str file_name)
