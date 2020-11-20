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

import async_channel.channels as channels
import async_channel.enums as channel_enums

import octobot_commons.channels_name as channels_name
import octobot_commons.list_util as list_util
import octobot_commons.logging as logging


class ChannelsManager:
    DEFAULT_REFRESH_TIMEOUT = 5

    def __init__(self, exchange_ids, matrix_id, refresh_timeout=DEFAULT_REFRESH_TIMEOUT):
        self.logger = logging.get_logger(self.__class__.__name__)
        self.exchange_ids = exchange_ids
        self.matrix_id = matrix_id
        self.refresh_timeout = refresh_timeout
        self.producers = []

    async def initialize(self) -> None:
        """
        Initialize Backtesting channels manager
        """
        self.logger.debug("Initializing producers...")
        try:
            self.producers = list_util.flatten_list(_get_backtesting_producers() +
                                                    self._get_trading_producers() +
                                                    self._get_evaluator_producers())

            # Initialize all producers by calling producer.start()
            for producer in list_util.flatten_list(self._get_trading_producers() + self._get_evaluator_producers()):
                await producer.start()
        except Exception as exception:
            self.logger.exception(exception, True, f"Error when initializing backtesting: {exception}")
            raise

    async def handle_new_iteration(self) -> None:
        for level_key in channel_enums.ChannelConsumerPriorityLevels:
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
        import octobot_trading.exchange_channel as exchange_channel
        return [
            _get_channel_producers(exchange_channel.get_chan(channel_name.value, exchange_id))
            for exchange_id in self.exchange_ids
            for channel_name in channels_name.OctoBotTradingChannelsName
        ]

    def _get_evaluator_producers(self):
        import octobot_evaluators.evaluators.channel as evaluators_channel
        return [
            _get_channel_producers(evaluators_channel.get_chan(channel_name.value, self.matrix_id))
            for channel_name in channels_name.OctoBotEvaluatorsChannelsName
        ]


def _get_channel_producers(channel):
    if channel.producers:
        return channel.producers
    return [channel.get_internal_producer()]


def _get_backtesting_producers():
    return [
        _get_channel_producers(channels.get_chan(channel_name.value))
        for channel_name in channels_name.OctoBotBacktestingChannelsName
    ]


def _check_producers_consumers_emptiness(producers, priority_level):
    for producer in producers:
        if not producer.is_consumers_queue_empty(priority_level):
            return False
    return True
