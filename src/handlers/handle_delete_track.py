import json

from src.common.utils import http_timer
from src.clients.cassandraclient import CassandraClient


@http_timer
def handle_delete_track(req: dict, cassandra_client: CassandraClient) -> dict:
    track_id = req.get("id")
    cassandra_client.delete_track(track_id)
    return {}