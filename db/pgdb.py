from typing import Tuple, List

import psycopg2


class PostgresqlClient:
    def __init__(self, database, user, password, host, port):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_insert(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()

    def execute_insert_many(self, query, params: List[Tuple]):
        self.cursor.executemany(query, params)
        self.conn.commit()

    def execute_delete(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

