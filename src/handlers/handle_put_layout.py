import json, logging

from src.common.utils import http_timer
from src.common.httpcontext import HttpContext
from src.clients.cassandraclient import CassandraClient


logger = logging.getLogger(__name__)


@http_timer
def handle_put_layout(req: dict, ctx: HttpContext, cassandra_client: CassandraClient) -> dict:
    layout_id = req.get("layoutId")
    layout = cassandra_client.get_layout(layout_id)
    if not layout:
        raise ValueError(f"Layout with ID {layout_id} not found")
    data = layout.layoutdata

    counter = data["counter"]
    result_instance_id = None
    if "addTrack" in req:
        sub_req: dict = req["addTrack"]
        track_id: str = sub_req.get("trackId")
        instance_id: str = sub_req.get("instanceId")
        x: float = sub_req.get("x")
        y: float = sub_req.get("y")
        rotation: float = sub_req.get("rotation")
        if not track_id or x is None or y is None or rotation is None:
            raise ValueError(f"Missing parameters for addTrack: trackId={track_id} x={x} y={y} rotation={rotation}")
        logger.info(f"Adding/updating track {track_id} at ({x},{y}) rotation={rotation} instanceId={instance_id}")
        
        # If instanceId provided, update existing track
        if instance_id:
            track_found = False
            for track in data["tracks"]:
                if track["instanceId"] == instance_id:
                    track["x"] = x
                    track["y"] = y
                    track["rotation"] = rotation
                    track_found = True
                    result_instance_id = instance_id
                    break
            if not track_found:
                raise ValueError(f"Track instance {instance_id} not found in layout")
        else:
            # Create new track with new instanceId
            counter += 1
            data["counter"] = counter
            new_instance_id = f"track-{track_id}-{counter}"
            data["tracks"].append({
                "instanceId": new_instance_id,
                "trackId": track_id,
                "x": x,
                "y": y,
                "rotation": rotation,
                "fixed": False
            })
            result_instance_id = new_instance_id

    if "fixTrack" in req:
        sub_req: dict = req["fixTrack"]
        instance_id: str = sub_req.get("instanceId")
        fixed: bool = sub_req.get("fixed", True)
        if not instance_id:
            raise ValueError("Missing instanceId for fixTrack")
        logger.info(f"Setting fixed={fixed} for track with instanceId={instance_id}")
        
        # Update fixed status for track
        track_found = False
        for track in data["tracks"]:
            if track["instanceId"] == instance_id:
                track["fixed"] = fixed
                track_found = True
                break
        
        if not track_found:
            raise ValueError(f"Track instance {instance_id} not found in layout")

    if "removeTrack" in req:
        sub_req: dict = req["removeTrack"]
        instance_id: str = sub_req.get("instanceId")
        if not instance_id:
            raise ValueError("Missing instanceId for removeTrack")
        logger.info(f"Removing track with instanceId={instance_id}")
        
        # Remove track with matching instanceId
        original_count = len(data["tracks"])
        data["tracks"] = [track for track in data["tracks"] if track["instanceId"] != instance_id]
        
        if len(data["tracks"]) == original_count:
            raise ValueError(f"Track instance {instance_id} not found in layout")

    layout.layoutdata = data
    cassandra_client.update_layout(layout)
    return {"instanceId": result_instance_id} if result_instance_id else {}