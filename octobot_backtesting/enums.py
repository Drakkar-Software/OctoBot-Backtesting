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
from enum import Enum


class BacktestingDataFormats(Enum):
    REGULAR_COLLECTOR_DATA = 0
    KAIKO_DATA = 1


class BacktestingDataFormatKeys(Enum):
    SYMBOL = "symbol"
    EXCHANGE = "exchange"
    DATE = "date"
    CANDLES = "candles"
    TYPE = "type"


class BacktestingReportFormat(Enum):
    SYMBOL_REPORT = "symbol_report"
    BOT_REPORT = "bot_report"
    SYMBOLS_WITH_TF = "symbols_with_time_frames_frames"
