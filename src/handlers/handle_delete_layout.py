import json

from src.common.utils import http_timer
from src.clients.cassandraclient import CassandraClient


@http_timer
def handle_delete_layout(req: dict, cassandra_client: CassandraClient) -> dict:
    layout_id = req.get("id")
    cassandra_client.delete_layout(layout_id)
    return {}