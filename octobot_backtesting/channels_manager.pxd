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

cdef class ChannelsManager:
    cdef object logger

    cdef list exchange_ids
    cdef list producers

    cdef str matrix_id

    cdef int refresh_timeout

    cpdef void flush(self)

    cdef list _get_trading_producers(self)
    cdef list _get_evaluator_producers(self)

cdef bint _check_producers_consumers_emptiness(list producers, int priority_level)
cdef list _get_backtesting_producers()
cdef list _get_channel_producers(object channel)
