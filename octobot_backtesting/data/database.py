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
from octobot_commons.logging.logging_util import get_logger
import sqlite3


class DataBase:
    TIMESTAMP_COLUMN = "timestamp"
    DEFAULT_ORDER_BY = TIMESTAMP_COLUMN
    DEFAULT_SORT = "DESC"
    DEFAULT_WHERE_OPERATION = "="
    DEFAULT_SIZE = -1

    def __init__(self, file_name):
        self.file_name = file_name
        self.logger = get_logger(self.__class__.__name__)

        self.connection = sqlite3.connect(self.file_name)
        self.cursor = self.connection.cursor()
        self.tables = []
        self.__init_tables_list()

    def insert(self, table, timestamp, **kwargs):
        if table.value not in self.tables:
            self.__create_table(table, **kwargs)

        # Insert a row of data
        inserting_values = [f"'{value}'" for value in kwargs.values()]
        self.__insert_values(table, timestamp, ', '.join(inserting_values))

        # Save (commit) the changes
        self.connection.commit()

    def __insert_values(self, table, timestamp, inserting_values):
        self.cursor.execute(f"INSERT INTO {table.value} VALUES ({timestamp}, {inserting_values})")

    def select(self, table, size=DEFAULT_SIZE, order_by=DEFAULT_ORDER_BY, sort=DEFAULT_SORT, **kwargs):
        return self.__execute_select(table=table,
                                     where_clauses=self.__where_clauses_from_kwargs(**kwargs),
                                     additional_clauses=self.__select_order_by(order_by, sort),
                                     size=size)

    def select_from_timestamp(self, table, timestamps: list, operations: list,
                              size=DEFAULT_SIZE, order_by=DEFAULT_ORDER_BY, sort=DEFAULT_SORT, **kwargs):
        timestamps_where_clauses = self.__where_clauses_from_operations(keys=[self.TIMESTAMP_COLUMN] * len(timestamps),
                                                                        values=timestamps,
                                                                        operations=operations)
        return self.__execute_select(table=table,
                                     where_clauses=f"{self.__where_clauses_from_kwargs(**kwargs)} "
                                                   f"AND "
                                                   f"{timestamps_where_clauses}",
                                     additional_clauses=self.__select_order_by(order_by, sort),
                                     size=size)

    def __where_clauses_from_kwargs(self, **kwargs) -> str:
        return self.__where_clauses_from_operations(list(kwargs.keys()), list(kwargs.values()), [])

    def __where_clauses_from_operation(self, key, value, operation=DEFAULT_WHERE_OPERATION):
        return f"{key} {operation if operation is not None else self.DEFAULT_WHERE_OPERATION} '{value}'"

    def __where_clauses_from_operations(self, keys, values, operations):
        return " AND ".join([self.__where_clauses_from_operation(keys[i],
                                                                 values[i],
                                                                 operations[i] if len(operations) > i else None)
                             for i in range(len(keys))
                             if values[i] is not None])

    def __select_order_by(self, order_by, sort):
        return f"ORDER BY " \
               f"{order_by if order_by is not None else self.DEFAULT_ORDER_BY} " \
               f"{sort if sort is not None else self.DEFAULT_SORT}"

    def __execute_select(self, table, select_items="*", where_clauses="", additional_clauses="", size=DEFAULT_SIZE):
        self.cursor.execute(f"SELECT {select_items} FROM {table.value} WHERE {where_clauses} {additional_clauses}")
        return self.cursor.fetchall() if size == self.DEFAULT_SIZE else self.cursor.fetchmany(size)

    def __check_table_exists(self, table) -> bool:
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table.value}'")
        return self.cursor.fetchall() != []

    def __create_table(self, table, **kwargs) -> None:
        try:
            self.cursor.execute(
                f"CREATE TABLE {table.value} ({self.TIMESTAMP_COLUMN} datetime, {' text, '.join([col for col in kwargs.keys()])})")
        except sqlite3.OperationalError:
            self.logger.error(f"{table} already exists")
        finally:
            self.tables.append(table.value)

    def __init_tables_list(self):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table'")
        self.tables = self.cursor.fetchall()

    def stop(self):
        self.connection.close()
