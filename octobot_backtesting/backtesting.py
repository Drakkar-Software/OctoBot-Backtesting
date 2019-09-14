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
from octobot_commons.enums import PriceIndexes
from octobot_commons.logging.logging_util import get_logger
import os
import time

from octobot_commons.pretty_printer import PrettyPrinter

from octobot_backtesting import CONFIG_BACKTESTING, CONFIG_ANALYSIS_ENABLED_OPTION
from octobot_trading.constants import CONFIG_CRYPTO_CURRENCIES, CONFIG_CRYPTO_PAIRS


class Backtesting:
    def __init__(self, config, exchange_simulator, exit_at_end=True):
        self.config = config
        self.begin_time = time.time()
        self.force_exit_at_end = exit_at_end
        self.exchange_simulator = exchange_simulator
        self.logger = get_logger(self.__class__.__name__)
        self.ended_symbols = set()
        self.symbols_to_test = set()

        self.__init_symbols_to_test()

    def get_is_finished(self, symbols=None):
        if symbols is None:
            return len(self.ended_symbols) == len(self.symbols_to_test)
        else:
            return all(symbol in self.ended_symbols for symbol in symbols)

    async def end(self, symbol):
        self.ended_symbols.add(symbol)
        if self.get_is_finished():
            try:
                self.logger.info(" **** Backtesting report ****")
                self.logger.info(" ========= Trades =========")

                self.logger.info(" ========= Symbols price evolution =========")

                self.logger.info(" ========= Octobot end state =========")
            except AttributeError:
                self.logger.info(" *** Backtesting ended ****")

            if self.force_exit_at_end:
                if self.analysis_enabled(self.config):
                    self.logger.info(" *** OctoBot will now keep working for analysis purposes because of the '-ba' "
                                     "(--backtesting_analysis) argument. To stop it, use CTRL+C or 'STOP OCTOBOT' "
                                     "from the web interface. ***")
                else:
                    os._exit(0)

    async def _get_symbol_report(self, symbol, trader):
        market_data = self.exchange_simulator.get_ohlcv(symbol)[self.exchange_simulator.MIN_ENABLED_TIME_FRAME.value]

        # profitability
        total_profitability = 0
        _, profitability, _, _, _ = await trader.get_trades_manager().get_profitability()
        total_profitability += profitability

        # vs market
        return self.get_market_delta(market_data)

    def __init_symbols_to_test(self):
        for crypto_currency_data in self.config[CONFIG_CRYPTO_CURRENCIES].values():
            for symbol in crypto_currency_data[CONFIG_CRYPTO_PAIRS]:
                if symbol in self.exchange_simulator.symbols:
                    self.symbols_to_test.add(symbol)

    @staticmethod
    def get_market_delta(market_data):
        market_begin = market_data[0][PriceIndexes.IND_PRICE_CLOSE.value]
        market_end = market_data[-1][PriceIndexes.IND_PRICE_CLOSE.value]

        if market_begin and market_end and market_begin > 0:
            market_delta = market_end / market_begin - 1 if market_end >= market_begin \
                else 1 - market_begin / market_end
        else:
            market_delta = 0

        return market_delta

    @staticmethod
    def analysis_enabled(config):
        return CONFIG_BACKTESTING in config and config[CONFIG_BACKTESTING][CONFIG_ANALYSIS_ENABLED_OPTION]
