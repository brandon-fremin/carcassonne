from src.common.utils import http_timer

@http_timer
def handle_ping(req: dict) -> dict:
    return {"status": "ok", "message": "Server is running", "data": req}