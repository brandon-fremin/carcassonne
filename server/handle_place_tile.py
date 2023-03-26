import random
from utils.state import get_state 
from utils.move import move_from_json
from utils.get_legal_moves import get_legal_moves

def handle_place_tile(request: dict) -> dict:
    state = get_state()
    move = move_from_json(request)

    # check if move is illegal
    if move not in state.legalMoves:
        err = f"Illegal move: '{move}'"
        print(err)
        return { "error": err }

    # clear unplayable flag
    for tile in state.tiles:
        tile.isUnplayable = False

    # update tile
    for tile in state.tiles:
        if tile == state.nextTile:
            tile.i = move.i
            tile.j = move.j
            tile.rotate(move.rot)
            break
    
    # Update board, nextTile, and legalMoves
    game_over = state.update_from_tiles()

    # save state to .json files
    state.save()

    # return resposne to client
    return state.client_json()