import json, random

from src.common.utils import http_timer, hash
from src.common.httpcontext import HttpContext
from src.clients.cassandraclient import CassandraClient, LayoutRecord


@http_timer
def handle_create_layout(req: dict, ctx: HttpContext, cassandra_client: CassandraClient) -> dict:
    layout_name = req.get("layoutName")
    if not layout_name:
        layout_name = "Untitled Layout"
    layout_id = hash(random.randint(0, 10 ** 9))
    layout_metadata = ctx.json()
    layout_data = {
        "counter": 0,
        "tracks": []
    }
    layout = LayoutRecord(
        id=layout_id,
        name=layout_name,
        layoutdata=layout_data,
        metadata=layout_metadata
    )
    created = cassandra_client.create_layout(layout)
    if not created:
        return {
            "error": f"Layout with the same ID already exists. {layout_id}"
        }
    return {
        "layoutId": layout_id
    }