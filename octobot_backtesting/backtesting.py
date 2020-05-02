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
from octobot_backtesting.channels import TIME_CHANNEL
from octobot_backtesting.channels.time import TimeChannel
from octobot_channels.channels.channel import get_chan, set_chan, del_chan

from octobot_backtesting.producers.time_updater import TimeUpdater
from octobot_channels.util.channel_creator import create_channel_instance
from octobot_commons.logging.logging_util import get_logger

from octobot_backtesting.data_manager.time_manager import TimeManager
from octobot_backtesting.util.backtesting_util import create_importer_from_backtesting_file_name
from octobot_commons.tentacles_management.class_inspector import default_parents_inspection


class Backtesting:
    def __init__(self, config, exchange_ids, matrix_id, backtesting_files):
        self.config = config
        self.backtesting_files = backtesting_files
        self.logger = get_logger(self.__class__.__name__)

        self.exchange_ids = exchange_ids
        self.matrix_id = matrix_id

        self.importers = []
        self.time_manager = None
        self.time_updater = None
        self.time_channel = None

    async def initialize(self):
        try:
            self.time_manager = TimeManager(config=self.config)
            self.time_manager.initialize()

            self.time_channel = await create_channel_instance(TimeChannel, set_chan, is_synchronized=True)

            self.time_updater = TimeUpdater(get_chan(TIME_CHANNEL), self)
        except Exception as e:
            self.logger.exception(e, True, f"Error when initializing backtesting : {e}.")

    async def stop(self):
        await self.delete_time_channel()
        self.time_updater.backtesting = None

    async def delete_time_channel(self):
        await self.time_channel.stop()
        for consumer in self.time_channel.consumers:
            await self.time_channel.remove_consumer(consumer)
        self.time_channel.flush()
        del_chan(self.time_channel.get_name())

    async def start_time_updater(self):
        await self.time_updater.run()

    async def create_importers(self):
        try:
            self.importers = [await create_importer_from_backtesting_file_name(self.config, backtesting_file)
                              for backtesting_file in self.backtesting_files]
        except TypeError:
            pass

    async def handle_time_update(self, timestamp):
        if self.time_manager:
            self.time_manager.set_current_timestamp(timestamp)

    def get_importers(self, importer_parent_class=None) -> list:
        return [importer
                for importer in self.importers
                if default_parents_inspection(importer.__class__, importer_parent_class)] \
            if importer_parent_class is not None else self.importers

    def get_progress(self):
        if self._has_nothing_to_do():
            return 0
        return 1 - (self.time_manager.get_remaining_iteration() / self.time_manager.get_total_iteration())

    def is_in_progress(self):
        if self._has_nothing_to_do():
            return False
        else:
            return self.time_manager.get_remaining_iteration() > 0

    def _has_nothing_to_do(self):
        return not self.time_manager or self.time_manager.get_total_iteration() == 0
