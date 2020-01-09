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
from octobot_channels.channels.channel import get_chan, set_chan

from octobot_backtesting.producers.time_updater import TimeUpdater
from octobot_channels.util import create_channel_instance
from octobot_commons.logging.logging_util import get_logger

from octobot_backtesting.data_manager.time_manager import TimeManager
from octobot_backtesting.util.backtesting_util import create_importer_from_backtesting_file_name
from octobot_commons.tentacles_management import default_parents_inspection


class Backtesting:
    def __init__(self, config, backtesting_files):
        self.config = config
        self.backtesting_files = backtesting_files
        self.logger = get_logger(self.__class__.__name__)

        self.importers = []
        self.time_manager = None

    async def initialize(self):
        try:
            self.time_manager = TimeManager(self.config)
            self.time_manager.initialize()

            await create_channel_instance(TimeChannel, set_chan)

            await TimeUpdater(get_chan(TIME_CHANNEL), self).run()
        except Exception as e:
            self.logger.error(f"Error when initializing backtesting : {e}.")
            self.logger.exception(e)

    async def create_importers(self):
        self.importers = [await create_importer_from_backtesting_file_name(self.config, backtesting_file)
                          for backtesting_file in self.backtesting_files]

    async def handle_time_update(self, timestamp):
        if self.time_manager:
            self.time_manager.set_current_timestamp(timestamp)

    def get_importers(self, importer_parent_class=None) -> list:
        return [importer
                for importer in self.importers
                if default_parents_inspection(importer.__class__, importer_parent_class)] if importer_parent_class is not None else self.importers

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
