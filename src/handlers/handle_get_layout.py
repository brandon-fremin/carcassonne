from src.common.utils import http_timer
from src.clients.cassandraclient import CassandraClient


@http_timer
def handle_get_layout(req: dict, cassandra_client: CassandraClient) -> dict:
    layouts = cassandra_client.get_layouts()
    result = []
    for layout in layouts:
        result.append({
            "id": layout.id,
            "name": layout.name,
            "data": layout.layoutdata,
            "metadata": layout.metadata
        })
    return {
        "layouts": result
    }