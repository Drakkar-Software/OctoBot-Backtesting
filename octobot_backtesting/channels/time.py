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
from asyncio import CancelledError

from octobot_channels.channels.channel import Channel
from octobot_channels.consumer import SupervisedConsumer
from octobot_channels.producer import Producer


class TimeProducer(Producer):
    def __init__(self, channel, backtesting):
        super().__init__(channel)
        self.backtesting = backtesting

    async def push(self, timestamp):
        await self.perform(timestamp)

    async def perform(self, timestamp):
        try:
            await self.backtesting.handle_time_update(timestamp)
            await self.send(timestamp)
        except CancelledError:
            self.logger.info("Update tasks cancelled.")
        except Exception as e:
            self.logger.exception(e, True, f"Exception when triggering time update: {e}")

    async def send(self, timestamp, **kwargs):
        for consumer in self.channel.get_consumer_from_filters({}):
            await consumer.queue.put({
                "timestamp": timestamp
            })


class TimeConsumer(SupervisedConsumer):
    pass


class TimeChannel(Channel):
    PRODUCER_CLASS = TimeProducer
    CONSUMER_CLASS = TimeConsumer
