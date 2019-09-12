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

    def select(self, table, size=-1, sort="ASC", **kwargs):
        where_clauses = [f"{key} = '{value}'" for key, value in kwargs.items()]
        self.cursor.execute(f"SELECT * FROM {table.value} WHERE {','.join(where_clauses)} ORDER BY timestamp {sort}")
        return self.cursor.fetchall() if size == -1 else self.cursor.fetchmany(size)

    def stop(self):
        self.connection.close()

    def __check_table_exists(self, table) -> bool:
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table.value}'")
        return self.cursor.fetchall() != []

    def __create_table(self, table, **kwargs) -> None:
        try:
            self.cursor.execute(
                f"CREATE TABLE {table.value} (timestamp datetime, {' text, '.join([col for col in kwargs.keys()])})")
        except sqlite3.OperationalError:
            self.logger.error(f"{table} already exists")
        finally:
            self.tables.append(table.value)

    def __init_tables_list(self):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table'")
        self.tables = self.cursor.fetchall()
