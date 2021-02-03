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


def get_available_data_types(importer) -> list:
    return importer.available_data_types


def get_available_time_frames(exchange_importer) -> list:
    return exchange_importer.time_frames


def get_available_symbols(exchange_importer) -> list:
    return exchange_importer.symbols


async def get_data_timestamp_interval(exchange_importer, time_frame=None) -> (float, float):
    time_frame_value = time_frame.value if time_frame is not None else None
    return await exchange_importer.get_data_timestamp_interval(time_frame=time_frame_value)


async def stop_importer(importer) -> None:
    await importer.stop()
