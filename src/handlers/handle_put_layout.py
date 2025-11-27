import json, logging, math

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
            old_track = None
            for track in data["tracks"]:
                if track["instanceId"] == instance_id:
                    old_track = track.copy()
                    track_found = True
                    result_instance_id = instance_id
                    break
            
            if not track_found:
                raise ValueError(f"Track instance {instance_id} not found in layout")
            
            # Calculate delta from old position to new position
            delta_x = x - old_track["x"]
            delta_y = y - old_track["y"]
            rotation_delta = rotation - old_track["rotation"]
            
            # Find all connected tracks recursively
            def get_connected_tracks(start_instance_id: str, visited: set = None) -> set:
                if visited is None:
                    visited = set()
                
                if start_instance_id in visited:
                    return visited
                    
                visited.add(start_instance_id)
                
                # Find the track
                track = next((t for t in data["tracks"] if t["instanceId"] == start_instance_id), None)
                if not track or track.get("fixed", False):
                    return visited
                
                # Get all linked tracks
                links = track.get("links", [])
                for link in links:
                    target_id = link.get("targetInstanceId")
                    if target_id:
                        target_track = next((t for t in data["tracks"] if t["instanceId"] == target_id), None)
                        if target_track and not target_track.get("fixed", False):
                            get_connected_tracks(target_id, visited)
                
                return visited
            
            # Get all connected tracks
            connected_instance_ids = get_connected_tracks(instance_id)
            
            # Calculate rotation transformation if rotation changed
            rotation_delta_rad = math.radians(rotation_delta)
            cos_delta = math.cos(rotation_delta_rad)
            sin_delta = math.sin(rotation_delta_rad)
            pivot_x = old_track["x"]
            pivot_y = old_track["y"]
            
            # Update positions and rotations of all connected tracks
            for track in data["tracks"]:
                if track["instanceId"] in connected_instance_ids:
                    if track["instanceId"] == instance_id:
                        # Main track: apply new position and rotation
                        track["x"] = x
                        track["y"] = y
                        track["rotation"] = rotation
                    else:
                        # Connected tracks: rotate around pivot, then translate
                        # 1. Get position relative to old pivot
                        rel_x = track["x"] - pivot_x
                        rel_y = track["y"] - pivot_y
                        
                        # 2. Rotate the relative position
                        rotated_rel_x = rel_x * cos_delta - rel_y * sin_delta
                        rotated_rel_y = rel_x * sin_delta + rel_y * cos_delta
                        
                        # 3. Translate to new position (old pivot + delta + rotated offset)
                        track["x"] = x + rotated_rel_x
                        track["y"] = y + rotated_rel_y
                        
                        # 4. Update rotation by the same delta
                        track["rotation"] = (track["rotation"] + rotation_delta) % 360
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
                "fixed": False,
                "links": []
            })
            result_instance_id = new_instance_id

    if "linkTrack" in req:
        sub_req: dict = req["linkTrack"]
        stationary_instance_id: str = sub_req.get("stationaryInstanceId")
        stationary_anchor_id: str = sub_req.get("stationaryAnchorId")
        moved_instance_id: str = sub_req.get("movedInstanceId")
        moved_anchor_id: str = sub_req.get("movedAnchorId")
        
        if not all([stationary_instance_id, stationary_anchor_id, moved_instance_id, moved_anchor_id]):
            raise ValueError("Missing parameters for linkTrack")
        
        logger.info(f"Linking tracks: {stationary_instance_id}:{stationary_anchor_id} <-> {moved_instance_id}:{moved_anchor_id}")
        
        # Log current state before linking
        logger.info(f"BEFORE LINK - All tracks in layout:")
        for t in data["tracks"]:
            logger.info(f"  {t['instanceId']}: pos=({t['x']},{t['y']}), links={t.get('links', [])}")
        
        # Find both tracks
        stationary_track = None
        moved_track = None
        for track in data["tracks"]:
            if track["instanceId"] == stationary_instance_id:
                stationary_track = track
            if track["instanceId"] == moved_instance_id:
                moved_track = track
        
        if not stationary_track:
            raise ValueError(f"Stationary track instance {stationary_instance_id} not found in layout")
        if not moved_track:
            raise ValueError(f"Moved track instance {moved_instance_id} not found in layout")
        
        # Get track data (with anchors) from database
        all_tracks = cassandra_client.get_tracks()
        stationary_track_data = next((t for t in all_tracks if t.id == stationary_track["trackId"]), None)
        moved_track_data = next((t for t in all_tracks if t.id == moved_track["trackId"]), None)
        
        if not stationary_track_data or not moved_track_data:
            raise ValueError("Track data not found in database")
        
        # Find the specific anchors
        stationary_anchor = next((a for a in stationary_track_data.trackdata.get("anchors", []) if a["id"] == stationary_anchor_id), None)
        moved_anchor = next((a for a in moved_track_data.trackdata.get("anchors", []) if a["id"] == moved_anchor_id), None)
        
        if not stationary_anchor or not moved_anchor:
            raise ValueError("Anchor not found in track data")
        
        # Calculate stationary anchor's world position and angle
        stat_local_x = stationary_anchor["position"]["x"]
        stat_local_y = stationary_anchor["position"]["y"]
        stat_dir_x = stationary_anchor["direction"]["x"]
        stat_dir_y = stationary_anchor["direction"]["y"]
        
        stat_rotation_rad = math.radians(stationary_track["rotation"])
        stat_cos = math.cos(stat_rotation_rad)
        stat_sin = math.sin(stat_rotation_rad)
        
        # Rotate stationary anchor position
        stat_rotated_x = stat_local_x * stat_cos - stat_local_y * stat_sin
        stat_rotated_y = stat_local_x * stat_sin + stat_local_y * stat_cos
        
        # Translate to world position
        stat_world_x = stat_rotated_x + stationary_track["x"]
        stat_world_y = stat_rotated_y + stationary_track["y"]
        
        # Calculate stationary anchor's world angle
        stat_local_angle = math.atan2(stat_dir_y, stat_dir_x) * 180 / math.pi
        stat_world_angle = stat_local_angle + stationary_track["rotation"]
        
        # Calculate moved anchor's local properties
        moved_local_x = moved_anchor["position"]["x"]
        moved_local_y = moved_anchor["position"]["y"]
        moved_dir_x = moved_anchor["direction"]["x"]
        moved_dir_y = moved_anchor["direction"]["y"]
        moved_local_angle = math.atan2(moved_dir_y, moved_dir_x) * 180 / math.pi
        
        # Calculate rotation needed to align with stationary anchor (180 degrees opposite)
        target_angle = stat_world_angle + 180
        angle_diff = target_angle - moved_local_angle
        
        # Normalize angle difference to -180 to 180 range
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360
        
        new_rotation = angle_diff % 360
        
        # Calculate position after rotation
        new_rotation_rad = math.radians(new_rotation)
        new_cos = math.cos(new_rotation_rad)
        new_sin = math.sin(new_rotation_rad)
        rotated_x = moved_local_x * new_cos - moved_local_y * new_sin
        rotated_y = moved_local_x * new_sin + moved_local_y * new_cos
        
        # New track position = target position - rotated anchor offset
        new_x = stat_world_x - rotated_x
        new_y = stat_world_y - rotated_y
        
        # Calculate delta from old position to new position
        delta_x = new_x - moved_track["x"]
        delta_y = new_y - moved_track["y"]
        rotation_delta = new_rotation - moved_track["rotation"]
        
        logger.info(f"Delta for linkTrack: dx={delta_x}, dy={delta_y}, moved_track has {len(moved_track.get('links', []))} links")
        
        # Find all tracks connected to the moved track (before creating the new link)
        def get_connected_tracks_recursive(start_instance_id: str, visited: set) -> set:
            if start_instance_id in visited:
                return visited
                
            visited.add(start_instance_id)
            
            # Find the track
            track = next((t for t in data["tracks"] if t["instanceId"] == start_instance_id), None)
            if not track:
                return visited
                
            if track.get("fixed", False):
                visited.discard(start_instance_id)  # Remove fixed tracks from the set
                return visited
            
            # Get all linked tracks
            links = track.get("links", [])
            logger.info(f"Track {start_instance_id} has {len(links)} links: {[l.get('targetInstanceId') for l in links]}")
            for link in links:
                target_id = link.get("targetInstanceId")
                if target_id and target_id not in visited:
                    target_track = next((t for t in data["tracks"] if t["instanceId"] == target_id), None)
                    if target_track and not target_track.get("fixed", False):
                        get_connected_tracks_recursive(target_id, visited)
            
            return visited
        
        # Get all connected tracks
        connected_instance_ids = get_connected_tracks_recursive(moved_instance_id, set())
        logger.info(f"Found {len(connected_instance_ids)} connected tracks: {connected_instance_ids}")
        
        # Store old position of moved track as the pivot point for rotation
        old_moved_x = moved_track["x"]
        old_moved_y = moved_track["y"]
        old_moved_rotation = moved_track["rotation"]
        
        # Calculate rotation transformation
        rotation_delta_rad = math.radians(rotation_delta)
        cos_delta = math.cos(rotation_delta_rad)
        sin_delta = math.sin(rotation_delta_rad)
        
        # Update positions and rotations of all connected tracks
        for track in data["tracks"]:
            if track["instanceId"] in connected_instance_ids:
                if track["instanceId"] == moved_instance_id:
                    # The main moved track: apply translation and new rotation
                    track["x"] = new_x
                    track["y"] = new_y
                    track["rotation"] = new_rotation
                    logger.info(f"Main moved track {track['instanceId']}: pos=({new_x},{new_y}), rot={new_rotation}")
                else:
                    # Connected tracks: rotate around the moved track's old position, then translate
                    # 1. Get position relative to old pivot
                    rel_x = track["x"] - old_moved_x
                    rel_y = track["y"] - old_moved_y
                    
                    # 2. Rotate the relative position
                    rotated_rel_x = rel_x * cos_delta - rel_y * sin_delta
                    rotated_rel_y = rel_x * sin_delta + rel_y * cos_delta
                    
                    # 3. Translate to new pivot position
                    track["x"] = new_x + rotated_rel_x
                    track["y"] = new_y + rotated_rel_y
                    
                    # 4. Update rotation by the same delta
                    track["rotation"] = (track["rotation"] + rotation_delta) % 360
                    
                    logger.info(f"Connected track {track['instanceId']}: pos=({track['x']},{track['y']}), rot={track['rotation']}")
        
        # Initialize links arrays if they don't exist
        if "links" not in stationary_track:
            stationary_track["links"] = []
        if "links" not in moved_track:
            moved_track["links"] = []
        
        # Create link objects
        stationary_link = {
            "anchorId": stationary_anchor_id,
            "targetInstanceId": moved_instance_id,
            "targetAnchorId": moved_anchor_id
        }
        moved_link = {
            "anchorId": moved_anchor_id,
            "targetInstanceId": stationary_instance_id,
            "targetAnchorId": stationary_anchor_id
        }
        
        # Add links to both tracks (avoid duplicates)
        if stationary_link not in stationary_track["links"]:
            stationary_track["links"].append(stationary_link)
        if moved_link not in moved_track["links"]:
            moved_track["links"].append(moved_link)

    if "unlinkTrack" in req:
        sub_req: dict = req["unlinkTrack"]
        instance_id: str = sub_req.get("instanceId")
        x: float = sub_req.get("x")
        y: float = sub_req.get("y")
        if not instance_id:
            raise ValueError("Missing instanceId for unlinkTrack")
        logger.info(f"Unlinking track with instanceId={instance_id} at new position ({x},{y})")
        
        # Find the track
        track = next((t for t in data["tracks"] if t["instanceId"] == instance_id), None)
        if not track:
            raise ValueError(f"Track instance {instance_id} not found in layout")
        
        # Get all links from this track
        links_to_remove = track.get("links", [])
        
        # Remove links from connected tracks
        for link in links_to_remove:
            target_instance_id = link.get("targetInstanceId")
            target_anchor_id = link.get("targetAnchorId")
            if target_instance_id:
                target_track = next((t for t in data["tracks"] if t["instanceId"] == target_instance_id), None)
                if target_track and "links" in target_track:
                    # Remove the reverse link
                    target_track["links"] = [
                        l for l in target_track["links"] 
                        if not (l.get("targetInstanceId") == instance_id and l.get("targetAnchorId") == link.get("anchorId"))
                    ]
        
        # Clear all links from this track
        track["links"] = []
        
        # Update position if provided
        if x is not None and y is not None:
            track["x"] = x
            track["y"] = y

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