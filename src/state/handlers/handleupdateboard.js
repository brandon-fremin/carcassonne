export default function handleUpdateBoard(state, payload) {
  console.log("handleUpdateBoard")
  console.log("Old State", state)
  console.log("Payload", payload)

  const { board, nextTile, legalMoves } = payload

  let newState = { ...state }
  newState.board = board
  newState.nextTile = nextTile
  newState.legalMoves = legalMoves

  console.log("New State", newState)
  return newState
}
