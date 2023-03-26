from utils.state import get_state

def handle_get_state(request: dict) -> dict:
    state = get_state()
    return state.client_json()
