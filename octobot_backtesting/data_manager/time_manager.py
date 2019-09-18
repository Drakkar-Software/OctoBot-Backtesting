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
import time

from octobot_commons.logging.logging_util import get_logger


class TimeManager:
    TIMESTAMP_INIT_VALUE = -1
    DEFAULT_FINISH_TIME_DELTA = 1000
    TIME_INTERVAL = 1000000

    def __init__(self, config):
        self.logger = get_logger(self.__class__.__name__)
        self.config = config

        self.time_initialized = False

        self.starting_timestamp = self.TIMESTAMP_INIT_VALUE
        self.finishing_timestamp = self.TIMESTAMP_INIT_VALUE
        self.current_timestamp = self.TIMESTAMP_INIT_VALUE

    def initialize(self):
        self.__reset_time()
        self.time_initialized = True

    def start(self):
        if self.starting_timestamp == self.TIMESTAMP_INIT_VALUE:
            self.starting_timestamp = time.time()

        if self.finishing_timestamp == self.TIMESTAMP_INIT_VALUE:
            self.finishing_timestamp = self.starting_timestamp + self.DEFAULT_FINISH_TIME_DELTA

        self.current_timestamp = self.starting_timestamp

    def __reset_time(self):
        self.set_current_timestamp(0)

    def has_finished(self):
        return self.current_timestamp >= self.finishing_timestamp

    def next_timestamp(self):
        self.current_timestamp += self.TIME_INTERVAL

    def set_minimum_timestamp(self, minimum_timestamp):
        if self.starting_timestamp == self.TIMESTAMP_INIT_VALUE or self.starting_timestamp > minimum_timestamp:
            self.starting_timestamp = minimum_timestamp
            self.logger.info(f"Set minimum timestamp to : {minimum_timestamp}")

    def set_maximum_timestamp(self, maximum_timestamp):
        if self.finishing_timestamp == self.TIMESTAMP_INIT_VALUE or self.finishing_timestamp < maximum_timestamp:
            self.finishing_timestamp = maximum_timestamp
            self.logger.info(f"Set maximum timestamp to : {maximum_timestamp}")

    def set_current_timestamp(self, timestamp):
        self.current_timestamp = timestamp
        self.logger.info(f"Set timestamp to : {timestamp}")

    def get_total_iteration(self):
        return (self.finishing_timestamp - self.starting_timestamp) / self.TIME_INTERVAL

    def get_remaining_iteration(self):
        return (self.finishing_timestamp - self.current_timestamp) / self.TIME_INTERVAL
