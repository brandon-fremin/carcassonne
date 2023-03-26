export default function handlePreviewPlacement(state, payload) {
  console.log("handlePreviewPlacement")
  console.log("Old State", state)
  console.log("Payload", payload)

  const { i, j } = payload

  let newState = { ...state }
  newState.nextTile = { ...state.nextTile  }
  newState.nextTile.i = i
  newState.nextTile.j = j

  console.log("New State", newState)
  return newState
}