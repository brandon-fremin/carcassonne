export const ACTIONS = {
  PREVIEW_PLACEMENT: "PREVIEW_PLACEMENT",
  ROTATE_NEXT_TILE: "ROTATE_NEXT_TILE",
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
  newState.game.board.nextTile.transform.i = null
  newState.game.board.nextTile.transform.j = null
  return newState
}

const handleRotateNextTile = (state, payload) => {
  const { isClockwise } = payload
  let newState = { ...state }
  let newNextTile = { ...state.game.board.nextTile }
  const rot = newNextTile.transform.rot + 90 * (isClockwise ? -1 : 1)
  newNextTile.transform.rot = (rot + 360) % 360
  newState.game.board.nextTile = newNextTile
  return newState
}

const handlePreviewPlacement = (state, payload) => {
  const { i, j } = payload
  let newState = { ...state }
  let newNextTile = { ...state.game.board.nextTile }
  newNextTile.transform.i = i
  newNextTile.transform.j = j
  newState.game.board.nextTile = newNextTile
  return newState
}

const handler = (state, action) => {
  switch (action.type) {
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