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
import uuid
from sys import getrefcount
from asyncio import get_event_loop

from octobot_commons.logging.logging_util import get_logger


class OctoBotBacktesting:

    def __init__(self, backtesting_config,
                 tentacles_setup_config,
                 symbols_to_create_exchange_classes,
                 backtesting_files):
        self.logger = get_logger(self.__class__.__name__)
        self.backtesting_config = backtesting_config
        self.tentacles_setup_config = tentacles_setup_config
        self.bot_id = str(uuid.uuid4())
        self.matrix_id = ""
        self.exchange_manager_ids = []
        self.symbols_to_create_exchange_classes = symbols_to_create_exchange_classes
        self.evaluators = []
        self.service_feeds = []
        self.backtesting_files = backtesting_files
        self.backtestings = []

    async def initialize_and_run(self):
        self.logger.info(f"Starting on {self.backtesting_files} with {self.symbols_to_create_exchange_classes}")
        await self._init_evaluators()
        await self._init_service_feeds()
        await self._init_exchanges()
        await self._create_evaluators()
        await self._create_service_feeds()

    async def stop(self):
        self.logger.info(f"Stopping for {self.backtesting_files} with {self.symbols_to_create_exchange_classes}")
        try:
            exchange_managers = []
            from octobot_trading.api.exchange import get_exchange_managers_from_exchange_ids, stop_exchange
            from octobot_evaluators.api.matrix import del_matrix
            from octobot_evaluators.api.evaluators import stop_evaluator, stop_all_evaluator_channels
            from octobot_evaluators.api.initialization import del_evaluator_channels
            from octobot_services.api.service_feeds import stop_service_feed
            try:
                for exchange_manager in get_exchange_managers_from_exchange_ids(self.exchange_manager_ids):
                    exchange_managers.append(exchange_manager)
                    await stop_exchange(exchange_manager)
            except KeyError:
                # exchange managers are not added in global exchange list when an exception occurred
                pass
            for evaluators in self.evaluators:
                # evaluators by type
                for evaluator in evaluators:
                    # evaluator instance
                    if evaluator is not None:
                        await stop_evaluator(evaluator)
            await stop_all_evaluator_channels(self.matrix_id)
            del_evaluator_channels(self.matrix_id)
            del_matrix(self.matrix_id)
            for service_feed in self.service_feeds:
                await stop_service_feed(service_feed)

            to_reference_check = exchange_managers + self.backtestings
            # Call at the next loop iteration to first let coroutines get cancelled
            # (references to coroutine and caller objects are kept while in async loop)
            get_event_loop().call_soon(self.memory_leak_checkup, to_reference_check)
            self.backtestings = []

        except ImportError as e:
            self._log_import_error()
            raise e
        except Exception as e:
            self.logger.exception(e, True, f"Error when stopping independent backtesting: {e}")

    def memory_leak_checkup(self, to_check_elements):
        self.logger.debug(f"Memory leak checking {[e.__class__.__name__ for e in to_check_elements]}")
        for i in range(len(to_check_elements)):
            if getrefcount(to_check_elements[i]) > 2:
                # Using PyCharm debugger, right click on the element variable and use "Find references"
                # Warning: Python debugger can add references when watching an element
                element = to_check_elements[i]
                # Now expect 3 references because the above element variable adds a reference
                self.logger.error(f"Too many remaining references on the {element.__class__.__name__} element after "
                                  f"{self.__class__.__name__} run, the garbage collector won't free it "
                                  f"(expected a maximum of 3 references): {getrefcount(element)} actual references")

    # Use check_remaining_objects to check remaining objects from garbage collector after calling stop().
    # Warning: can take a long time when a lot of objects exist
    def check_remaining_objects(self):
        try:
            from octobot_trading.exchanges.data.exchange_symbol_data import ExchangeSymbolData
            from octobot_trading.exchanges.exchange_manager import ExchangeManager
            from octobot_trading.exchanges.exchange_simulator import ExchangeSimulator
            from octobot_trading.producers.simulator import OHLCVUpdaterSimulator
            import gc
            exchanges_count = len(self.exchange_manager_ids)
            to_watch_objects = (ExchangeSymbolData, ExchangeManager, ExchangeSimulator, OHLCVUpdaterSimulator)
            objects_references = {obj: 0 for obj in to_watch_objects}
            expected_max_objects_references = {
                ExchangeSymbolData: exchanges_count + 1,
                ExchangeManager: exchanges_count + 1,
                ExchangeSimulator: exchanges_count,
                OHLCVUpdaterSimulator: exchanges_count
            }
            for obj in gc.get_objects():
                if isinstance(obj, to_watch_objects):
                    objects_references[type(obj)] += 1

            for obj, max_ref in expected_max_objects_references.items():
                if objects_references[obj] > max_ref:
                    self._log_remaining_object_error(obj,
                                                     max_ref,
                                                     objects_references[obj])

        except ImportError as e:
            self._log_import_error()
            raise e

    def _log_remaining_object_error(self, obj, expected, actual):
        self.logger.error(f"Too many remaining {obj.__name__} instances: expected: {expected} actual {actual}")

    async def _init_evaluators(self):
        from octobot_evaluators.api.evaluators import initialize_evaluators
        from octobot_evaluators.api.initialization import create_evaluator_channels
        self.matrix_id = await initialize_evaluators(self.backtesting_config, self.tentacles_setup_config)
        await create_evaluator_channels(self.matrix_id)

    async def _init_service_feeds(self):
        try:
            from octobot_services.api.service_feeds import create_service_feed_factory
            service_feed_factory = create_service_feed_factory(self.backtesting_config,
                                                               get_event_loop(),
                                                               self.bot_id)
            self.service_feeds = [service_feed_factory.create_service_feed(feed)
                                  for feed in service_feed_factory.get_available_service_feeds(True)]
        except ImportError:
            self.logger.error("Octobot Services package is required to test service feeds. Service feeds will not "
                              "be available for this backtesting.")

    async def _create_evaluators(self):
        from octobot_evaluators.api.evaluators import create_all_type_evaluators
        from octobot_trading.api.exchange import get_exchange_configuration_from_exchange_id

        for exchange_id in self.exchange_manager_ids:
            exchange_configuration = get_exchange_configuration_from_exchange_id(exchange_id)
            self.evaluators = await create_all_type_evaluators(
                self.backtesting_config,
                self.tentacles_setup_config,
                matrix_id=self.matrix_id,
                exchange_name=exchange_configuration.exchange_name,
                bot_id=self.bot_id,
                symbols_by_crypto_currencies=exchange_configuration.symbols_by_crypto_currencies,
                symbols=exchange_configuration.symbols,
                time_frames=exchange_configuration.time_frames)

    async def _create_service_feeds(self):
        try:
            from octobot_services.api.service_feeds import start_service_feed
            for feed in self.service_feeds:
                if not await start_service_feed(feed, False):
                    self.logger.error(f"Failed to start {feed.get_name()}. Evaluators requiring this service feed "
                                      f"might not work properly")
        except ImportError:
            pass

    async def _init_exchanges(self):
        from octobot_trading.api.exchange import create_exchange_builder, get_exchange_manager_id
        from octobot.logger import init_exchange_chan_logger

        for exchange_class_string in self.symbols_to_create_exchange_classes.keys():
            exchange_builder = create_exchange_builder(self.backtesting_config, exchange_class_string) \
                .has_matrix(self.matrix_id) \
                .use_tentacles_setup_config(self.tentacles_setup_config) \
                .is_simulated() \
                .is_rest_only() \
                .is_backtesting(self.backtesting_files)
            try:
                exchange_manager = await exchange_builder.build()
                await init_exchange_chan_logger(exchange_manager.id)
            finally:
                # always save exchange manager ids and backtesting instances
                self.exchange_manager_ids.append(get_exchange_manager_id(exchange_builder.exchange_manager))
                self._register_backtesting(exchange_builder.exchange_manager)

    def _register_backtesting(self, exchange_manager):
        from octobot_trading.api.exchange import get_backtesting_instance
        backtesting = get_backtesting_instance(exchange_manager)
        if backtesting is not None:
            self.backtestings.append(backtesting)

    def _log_import_error(self):
        self.logger.error("OctoBotBacktesting requires OctoBot, OctoBot-Trading, OctoBot-Services "
                          "and OctoBot-Evaluators packages installed")
