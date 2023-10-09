import psycopg2


class PgDBClient:
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

    def execute_insert_many(self, query, params):
        self.cursor.executemany(query, params)
        self.conn.commit()

    def execute_delete(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()


# 示例用法
if __name__ == "__main__":
    db = PgDBClient(
        host="your_host",
        port="your_port",
        database="your_database_name",
        user="your_username",
        password="your_password",
    )

    # 查询示例
    result = db.execute_query("SELECT * FROM your_table_name")
    for row in result:
        print(row)

    # 插入示例
    insert_query = "INSERT INTO your_table_name (column1, column2) VALUES (%s, %s)"
    insert_params = ("value1", "value2")
    db.execute_insert(insert_query, insert_params)

    # 关闭连接
    db.close()
