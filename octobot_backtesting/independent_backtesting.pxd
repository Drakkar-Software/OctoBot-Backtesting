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


from octobot_backtesting.octobot_backtesting cimport OctoBotBacktesting

cdef class IndependentBacktesting:
    cdef public dict octobot_origin_config
    cdef public dict backtesting_config
    cdef public list backtesting_files

    cdef object logger

    cdef public str data_file_path
    cdef public dict symbols_to_create_exchange_classes
    cdef public float risk
    cdef public dict starting_portfolio
    cdef public dict fees_config

    cdef public OctoBotBacktesting octobot_backtesting

    cpdef bint is_in_progress(self)
    cpdef float get_progress(self)

    cdef void _init_default_config_values(self)
    cdef dict _get_exchange_report(self, str exchange_id, str reference_market, object trading_mode)
    cdef void _adapt_config(self)
    cdef str _find_reference_market(self)
    cdef void _add_config_default_backtesting_values(self)
    cdef void _add_crypto_currencies_config(self)
    cdef void _log_import_error(self)
