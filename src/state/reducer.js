import handleBoardResize from "./handlers/handleboardresize"
import handlePreviewPlacement from "./handlers/handlepreviewplacement";
import handleUpdateBoard from "./handlers/handleupdateboard";

export const ACTIONS = {
  BOARD_RESIZE: "BOARD_RESIZE",
  UPDATE_BOARD: "UPDATE_BOARD",
  PREVIEW_PLACEMENT: "PREVIEW_PLACEMENT",
  ROTATE_NEXT_TILE: "ROTATE_NEXT_TILE",

  // New ones below
  DEFAULT_GAME_SETTINGS: "DEFAULT_GAME_SETTINGS",
  SET_SESSION_ID: "SET_SESSION_ID",
  SET_GAME: "SET_GAME"
};

const handleDefaultGameSettings = (state, payload) => {
  let newState = {...state}
  newState.defaultGameSettings = payload
  return newState
}

const handleSetSessionId = (state, payload) => {
  let newState = {...state}
  newState.sessionId = payload.sessionId
  return newState
}

const handleSetGame = (state, payload) => {
  let newState = {...state}
  newState.game = payload
  return newState
}

const handleRotateNextTile = (state, payload) => {
  const { isClockwise } = payload
  let newState = { ...state }
  newState.nextTile =  { ...state.nextTile }
  const rot = newState.nextTile.rot + 90 * (isClockwise ? -1 : 1)
  newState.nextTile.rot = (rot + 360) % 360
  return newState
}

const handler = (state, action) => {
  switch (action.type) {
    case ACTIONS.BOARD_RESIZE:
      return handleBoardResize(state, action.payload)
    case ACTIONS.UPDATE_BOARD:
      return handleUpdateBoard(state, action.payload)
    case ACTIONS.PREVIEW_PLACEMENT:
      return handlePreviewPlacement(state, action.payload)
    case ACTIONS.ROTATE_NEXT_TILE:
      return handleRotateNextTile(state, action.payload)
    

    case ACTIONS.DEFAULT_GAME_SETTINGS:
      return handleDefaultGameSettings(state, action.payload)
    case ACTIONS.SET_SESSION_ID:
      return handleSetSessionId(state, action.payload)
    case ACTIONS.SET_GAME:
      return handleSetGame(state, action.payload)
    default: {
      console.log(`Unknown action: '${action.type}'`)
      return state
    }
  }
}

//Reducer to Handle Actions
const globalStateReducer = (state, action) => {
  console.log("Old State: ", state)
  console.log("Type: ", action.type, " Payload: ", action.payload)
  const newState = handler(state, action)
  console.log("New State: ", newState)
  return newState
};

export default globalStateReducer