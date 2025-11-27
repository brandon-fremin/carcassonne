import sqlite3

from src.common.utils import synchronized, to_json


class LionelClient:
    def __init__(self, uri: str = "file:lionel/Lionel_LCS.sqlite?mode=ro", threadsafe: bool = True):
        self._uri = uri
        self._connection = sqlite3.connect(uri, uri=True)
        self._connection.row_factory = sqlite3.Row

    @synchronized
    def read_table(self, table_name: str) -> list[dict]:
        cursor = self._connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        cursor.close()
        return [to_json(dict(row)) for row in rows]