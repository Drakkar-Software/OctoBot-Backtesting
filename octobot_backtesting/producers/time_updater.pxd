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
from octobot_backtesting.channels_manager.channels_manager cimport ChannelsManager
from octobot_backtesting.data_manager.time_manager cimport TimeManager

from octobot_backtesting.channels.time cimport TimeProducer

cdef class TimeUpdater(TimeProducer):
    cdef public TimeManager time_manager
    cdef public ChannelsManager channels_manager

    cdef public double starting_time
    cdef public double simulation_duration

    cdef public object finished_event
