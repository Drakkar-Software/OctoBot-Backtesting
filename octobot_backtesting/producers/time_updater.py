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
import time

from octobot_backtesting.channels.time import TimeProducer


class TimeUpdater(TimeProducer):
    def __init__(self, channel, backtesting):
        super().__init__(channel, backtesting)
        self.time_manager = backtesting.time_manager
        self.starting_time = time.time()

    async def start(self):
        await asyncio.sleep(0.1)  # TODO
        while not self.should_stop:
            try:
                await self.push(self.time_manager.current_timestamp)
                self.time_manager.next_timestamp()

                try:
                    await self.wait_for_processing()
                except asyncio.CancelledError:
                    self.logger.warning("Stopped during processing")

                self.logger.info(f"Progress : {round(self.backtesting.get_progress() * 100, 2)}%")

                if self.time_manager.has_finished():
                    self.logger.warning("Maximum timestamp hit, stopping...")
                    self.logger.warning(f"Last {time.time() - self.starting_time}s")
                    await self.stop()
            except Exception as e:
                self.logger.exception(f"Fail to update time : {e}")

    async def modify(self, set_timestamp=None, minimum_timestamp=None, maximum_timestamp=None) -> None:
        if set_timestamp is not None:
            self.time_manager.set_current_timestamp(set_timestamp)

        if minimum_timestamp is not None:
            self.time_manager.set_minimum_timestamp(minimum_timestamp)
            self.time_manager.set_current_timestamp(minimum_timestamp)

        if maximum_timestamp is not None:
            self.time_manager.set_maximum_timestamp(maximum_timestamp)
