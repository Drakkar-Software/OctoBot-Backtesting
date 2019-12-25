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
from octobot_backtesting.collectors.exchanges.exchange_collector import ExchangeDataCollector
from octobot_commons.tentacles_management.advanced_manager import get_single_deepest_child_class


async def collect_exchange_historical_data(config, exchange_name, symbols, time_frames=None):
    collector_class = get_single_deepest_child_class(ExchangeDataCollector)
    collector_instance = collector_class(config, exchange_name, symbols, time_frames)
    if time_frames is None:
        collector_instance.use_all_available_timeframes()
    collector_instance.initialize()
    await collector_instance.start()
    return collector_instance.file_path
