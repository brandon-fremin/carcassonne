import json

from src.common.utils import http_timer, hash
from src.common.httpcontext import HttpContext
from src.clients.cassandraclient import CassandraClient, TrackRecord


@http_timer
def handle_create_track(req: dict, ctx: HttpContext, cassandra_client: CassandraClient) -> dict:
    track_data = req.get("trackData")
    track_name = req.get("trackName")
    track_metadata = ctx.json()
    track_id = hash(track_data)
    track = TrackRecord(
        id=track_id,
        name=track_name,
        trackdata=track_data,
        metadata=track_metadata
    )
    created = cassandra_client.create_track(track)
    if not created:
        return {
            "error": f"Track with the same ID already exists. {track_id}"
        }
    return {
        "trackId": track_id
    }