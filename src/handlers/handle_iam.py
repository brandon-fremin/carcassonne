from src.common.httpcontext import HttpContext
from src.common.utils import http_timer

@http_timer
def handle_iam(context: HttpContext) -> dict:
    return context.json()