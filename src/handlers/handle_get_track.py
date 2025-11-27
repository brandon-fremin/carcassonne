import json

from src.common.utils import http_timer
from src.clients.cassandraclient import CassandraClient, TrackRecord


@http_timer
def handle_get_track(req: dict, cassandra_client: CassandraClient) -> dict:
    tracks = cassandra_client.get_tracks()
    result = []
    for track in tracks:
        result.append({
            "id": track.id,
            "name": track.name,
            "data": track.trackdata,
            "metadata": track.metadata
        })
    return {
        "tracks": result
    }