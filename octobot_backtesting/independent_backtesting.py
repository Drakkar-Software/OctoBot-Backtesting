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
from copy import deepcopy
from os import path

from octobot_backtesting.constants import CONFIG_BACKTESTING, BACKTESTING_FILE_PATH
from octobot_backtesting.data.data_file_manager import get_file_description
from octobot_backtesting.enums import DataFormatKeys
from octobot_backtesting.octobot_backtesting import OctoBotBacktesting
from octobot_commons.constants import CONFIG_ENABLED_OPTION, CONFIG_CRYPTO_CURRENCIES, CONFIG_CRYPTO_PAIRS
from octobot_commons.enums import PriceIndexes
from octobot_commons.errors import ConfigTradingError
from octobot_commons.logging.logging_util import get_logger
from octobot_commons.symbol_util import split_symbol
from octobot_commons.time_frame_manager import find_min_time_frame


class IndependentBacktesting:
    def __init__(self, config, backtesting_files, data_file_path=BACKTESTING_FILE_PATH):
        self.octobot_origin_config = config
        self.backtesting_config = {}
        self.backtesting_files = backtesting_files
        self.logger = get_logger(self.__class__.__name__)
        self.data_file_path = data_file_path
        self.symbols_to_create_exchange_classes = {}
        self.risk = 0.1
        self.starting_portfolio = {}
        self.fees_config = {}
        self.forced_time_frames = []
        self.forced_evaluators = []
        try:
            self._init_default_config_values()

        except ImportError as e:
            self._log_import_error()
            raise e
        self.octobot_backtesting = OctoBotBacktesting(self.backtesting_config,
                                                      self.symbols_to_create_exchange_classes,
                                                      self.backtesting_files)

    async def initialize_and_run(self, log_errors=True):
        try:
            await self.initialize_config()
            self._add_crypto_currencies_config()
            await self.octobot_backtesting.initialize_and_run()

        except ImportError as e:
            self._log_import_error()
            raise e
        except Exception as e:
            if log_errors:
                self.logger.error(f"Error when running backtesting: {e}")
                self.logger.exception(e)
            raise e

    async def initialize_config(self):
        await self._register_available_data()
        self._adapt_config()
        return self.backtesting_config

    async def join(self, timeout):
        finished_events = [asyncio.wait_for(backtesting.time_updater.finished_event.wait(), timeout)
                           for backtesting in self.octobot_backtesting.backtestings]
        await asyncio.gather(*finished_events)

    async def stop(self):
        await self.octobot_backtesting.stop()

    def is_in_progress(self):
        if self.octobot_backtesting.backtestings:
            return any([backtesting.is_in_progress() for backtesting in self.octobot_backtesting.backtestings])
        else:
            return False

    def get_progress(self):
        if self.octobot_backtesting.backtestings:
            return min([backtesting.get_progress() for backtesting in self.octobot_backtesting.backtestings])
        else:
            return 0

    @staticmethod
    def _get_market_delta(symbol, exchange_manager, min_timeframe):
        from octobot_trading.api.symbol_data import get_symbol_data, get_symbol_historical_candles
        market_data = get_symbol_historical_candles(get_symbol_data(exchange_manager, symbol), min_timeframe)
        market_begin = market_data[PriceIndexes.IND_PRICE_CLOSE.value][0]
        market_end = market_data[PriceIndexes.IND_PRICE_CLOSE.value][-1]

        if market_begin and market_end and market_begin > 0:
            market_delta = market_end / market_begin - 1 if market_end >= market_begin \
                else 1 - market_begin / market_end
        else:
            market_delta = 0

        return market_delta

    async def _register_available_data(self):
        for data_file in self.backtesting_files:
            description = await get_file_description(path.join(self.data_file_path, data_file))
            exchange_name = description[DataFormatKeys.EXCHANGE.value]
            if exchange_name not in self.symbols_to_create_exchange_classes:
                self.symbols_to_create_exchange_classes[exchange_name] = []
            for symbol in description[DataFormatKeys.SYMBOLS.value]:
                self.symbols_to_create_exchange_classes[exchange_name].append(symbol)

    def _init_default_config_values(self):
        from octobot_trading.constants import CONFIG_TRADER_RISK, CONFIG_TRADING, CONFIG_SIMULATOR, \
            CONFIG_STARTING_PORTFOLIO, CONFIG_SIMULATOR_FEES, CONFIG_EXCHANGES, CONFIG_TRADER
        from octobot_evaluators.constants import CONFIG_FORCED_TIME_FRAME, CONFIG_FORCED_EVALUATOR
        self.risk = deepcopy(self.octobot_origin_config[CONFIG_TRADING][CONFIG_TRADER_RISK])
        self.starting_portfolio = deepcopy(self.octobot_origin_config[CONFIG_SIMULATOR][CONFIG_STARTING_PORTFOLIO])
        self.fees_config = deepcopy(self.octobot_origin_config[CONFIG_SIMULATOR][CONFIG_SIMULATOR_FEES])
        if CONFIG_FORCED_TIME_FRAME in self.octobot_origin_config:
            self.forced_time_frames = deepcopy(self.octobot_origin_config[CONFIG_FORCED_TIME_FRAME])
        if CONFIG_FORCED_EVALUATOR in self.octobot_origin_config:
            self.forced_evaluators = deepcopy(self.octobot_origin_config[CONFIG_FORCED_EVALUATOR])
        self.backtesting_config = {
            CONFIG_BACKTESTING: {},
            CONFIG_CRYPTO_CURRENCIES: {},
            CONFIG_EXCHANGES: {},
            CONFIG_TRADER: {},
            CONFIG_SIMULATOR: {},
            CONFIG_TRADING: {},
        }

    async def get_dict_formatted_report(self):
        try:
            from octobot_trading.api.modes import get_activated_trading_mode
            from octobot_trading.api.profitability import get_reference_market
            reference_market = get_reference_market(self.backtesting_config)
            try:
                trading_mode = get_activated_trading_mode(self.backtesting_config).get_name()
            except ConfigTradingError as e:
                self.logger.error(e)
                trading_mode = "Error when reading trading mode"
            for exchange_id in self.octobot_backtesting.exchange_manager_ids:
                report = self._get_exchange_report(exchange_id, reference_market, trading_mode)
                # TODO: handle multi exchange reports
                return report
        except ImportError as e:
            self._log_import_error()
            raise e

    def _get_exchange_report(self, exchange_id, reference_market, trading_mode):
        try:
            from octobot_trading.api.exchange import get_exchange_manager_from_exchange_id, get_exchange_name, \
                get_watched_timeframes
            from octobot_trading.api.portfolio import get_portfolio, get_origin_portfolio
            from octobot_trading.api.profitability import get_profitability_stats
            SYMBOL_REPORT = "symbol_report"
            BOT_REPORT = "bot_report"
            CHART_IDENTIFIERS = "chart_identifiers"
            report = {
                SYMBOL_REPORT: [],
                BOT_REPORT: {},
                CHART_IDENTIFIERS: []
            }
            exchange_manager = get_exchange_manager_from_exchange_id(exchange_id)
            _, profitability, _, market_average_profitability, _ = get_profitability_stats(exchange_manager)
            min_timeframe = find_min_time_frame(get_watched_timeframes(exchange_manager))
            exchange_name = get_exchange_name(exchange_manager)
            for symbol in self.symbols_to_create_exchange_classes[exchange_name]:
                market_delta = self._get_market_delta(symbol, exchange_manager, min_timeframe)
                report[SYMBOL_REPORT].append({symbol: market_delta * 100})
                report[CHART_IDENTIFIERS].append({
                    "symbol": symbol,
                    "exchange_id": exchange_id,
                    "exchange_name": exchange_name,
                    "time_frame": min_timeframe.value
                })

            report[BOT_REPORT] = {
                "profitability": profitability,
                "market_average_profitability": market_average_profitability,
                "reference_market": reference_market,
                "end_portfolio": get_portfolio(exchange_manager),
                "starting_portfolio": get_origin_portfolio(exchange_manager),
                "trading_mode": trading_mode
            }
            return report
        except ImportError as e:
            self._log_import_error()
            raise e

    def _adapt_config(self):
        from octobot_trading.constants import CONFIG_TRADER_RISK, CONFIG_TRADING, CONFIG_SIMULATOR, \
            CONFIG_STARTING_PORTFOLIO, CONFIG_SIMULATOR_FEES,CONFIG_TRADER_REFERENCE_MARKET
        from octobot_evaluators.constants import CONFIG_FORCED_TIME_FRAME, CONFIG_FORCED_EVALUATOR
        self.backtesting_config[CONFIG_TRADING][CONFIG_TRADER_RISK] = self.risk
        self.backtesting_config[CONFIG_TRADING][CONFIG_TRADER_REFERENCE_MARKET] = self._find_reference_market()
        self.backtesting_config[CONFIG_SIMULATOR][CONFIG_STARTING_PORTFOLIO] = self.starting_portfolio
        self.backtesting_config[CONFIG_SIMULATOR][CONFIG_SIMULATOR_FEES] = self.fees_config
        if self.forced_time_frames:
            self.backtesting_config[CONFIG_FORCED_TIME_FRAME] = self.forced_time_frames
        if self.forced_evaluators:
            self.backtesting_config[CONFIG_FORCED_EVALUATOR] = self.forced_evaluators
        self._add_config_default_backtesting_values()

    def _find_reference_market(self):
        ref_market_candidate = None
        ref_market_candidates = {}
        for pairs in self.symbols_to_create_exchange_classes.values():
            for pair in pairs:
                base = split_symbol(pair)[1]
                if ref_market_candidate is None:
                    ref_market_candidate = base
                if base in ref_market_candidates:
                    ref_market_candidates[base] += 1
                else:
                    ref_market_candidates[base] = 1
                if ref_market_candidate != base and \
                   ref_market_candidates[ref_market_candidate] < ref_market_candidates[base]:
                    ref_market_candidate = base
        return ref_market_candidate

    def _add_config_default_backtesting_values(self):
        from octobot_trading.constants import CONFIG_TRADER, CONFIG_SIMULATOR
        if CONFIG_BACKTESTING not in self.backtesting_config:
            self.backtesting_config[CONFIG_BACKTESTING] = {}
        self.backtesting_config[CONFIG_BACKTESTING][CONFIG_ENABLED_OPTION] = True
        self.backtesting_config[CONFIG_TRADER][CONFIG_ENABLED_OPTION] = False
        self.backtesting_config[CONFIG_SIMULATOR][CONFIG_ENABLED_OPTION] = True

    def _add_crypto_currencies_config(self):
        for pairs in self.symbols_to_create_exchange_classes.values():
            for pair in pairs:
                if pair not in self.backtesting_config[CONFIG_CRYPTO_CURRENCIES]:
                    self.backtesting_config[CONFIG_CRYPTO_CURRENCIES][pair] = {
                        CONFIG_CRYPTO_PAIRS: []
                    }
                    self.backtesting_config[CONFIG_CRYPTO_CURRENCIES][pair][CONFIG_CRYPTO_PAIRS] = [pair]

    def _log_import_error(self):
        self.logger.error("Backtesting requires OctoBot-Trading package installed")
