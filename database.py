# database.py

import sqlite3
from typing import Optional


class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        print(f"Connected to database: {self.db_name}")

    def close(self):
        if self.connection:
            self.connection.close()
            print(f"Closed connection to database: {self.db_name}")

    def execute(self, query: str, params: Optional[list] = None):
        params = params or []
        if not self.connection:
            raise RuntimeError("Database connection is not established.")
        cursor = self.cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def create_all(self, tables: list):
        for table in tables:
            self.execute(table.create_table_sql())

    def get_conn(self):
        return DatabaseConnectionManager(self)


class DatabaseConnectionManager:
    def __init__(self, db: Database):
        self.db = db

    def __enter__(self):
        self.db.connect()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
