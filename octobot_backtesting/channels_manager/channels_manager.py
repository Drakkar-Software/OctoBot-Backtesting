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
import asyncio

from octobot_commons.enums import ChannelConsumerPriorityLevels
from octobot_channels.channels.channel import get_chan
from octobot_commons.channels_name import OctoBotEvaluatorsChannelsName, OctoBotTradingChannelsName, \
    OctoBotBacktestingChannelsName
from octobot_commons.list_util import flatten_list
from octobot_commons.logging.logging_util import get_logger


class ChannelsManager:
    DEFAULT_REFRESH_TIMEOUT = 5

    def __init__(self, exchange_ids, matrix_id, refresh_timeout=DEFAULT_REFRESH_TIMEOUT):
        self.logger = get_logger(self.__class__.__name__)
        self.exchange_ids = exchange_ids
        self.matrix_id = matrix_id
        self.refresh_timeout = refresh_timeout
        self.producers = []

    async def initialize(self) -> None:
        """
        Initialize Backtesting channels manager
        """
        self.logger.debug("Initializing producers...")
        self.producers = flatten_list(_get_backtesting_producers() +
                                      self._get_trading_producers() +
                                      self._get_evaluator_producers())

        # Initialize all producers by calling producer.start()
        for producer in flatten_list(self._get_trading_producers() + self._get_evaluator_producers()):
            await producer.start()

    async def handle_new_iteration(self) -> None:
        for level_key in ChannelConsumerPriorityLevels:
            try:
                await asyncio.wait_for(self.refresh_priority_level(level_key.value), timeout=self.refresh_timeout)
            except asyncio.TimeoutError:
                self.logger.error(f"Refreshing priority level {level_key.value} has been timed out.")

    async def refresh_priority_level(self, priority_level: int) -> None:
        while not _check_producers_consumers_emptiness(self.producers, priority_level):
            for producer in self.producers:
                await producer.synchronized_perform_consumers_queue(priority_level)

    def flush(self):
        self.producers = []

    def _get_trading_producers(self):
        from octobot_trading.channels.exchange_channel import get_chan as get_trading_chan
        return [
            _get_channel_producers(get_trading_chan(channel_name.value, exchange_id))
            for exchange_id in self.exchange_ids
            for channel_name in OctoBotTradingChannelsName
        ]

    def _get_evaluator_producers(self):
        from octobot_evaluators.channels.evaluator_channel import get_chan as get_evaluator_chan
        return [
            _get_channel_producers(get_evaluator_chan(channel_name.value, self.matrix_id))
            for channel_name in OctoBotEvaluatorsChannelsName
        ]


def _get_channel_producers(channel):
    if channel.producers:
        return channel.producers
    return [channel.get_internal_producer()]


def _get_backtesting_producers():
    return [
        _get_channel_producers(get_chan(channel_name.value))
        for channel_name in OctoBotBacktestingChannelsName
    ]


def _check_producers_consumers_emptiness(producers, priority_level):
    for producer in producers:
        if not producer.is_consumers_queue_empty(priority_level):
            return False
    return True
