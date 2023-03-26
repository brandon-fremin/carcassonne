export default function handleRotateNextTile(state, payload) {
  console.log("handleRotateNextTile")
  console.log("Old State", state)
  console.log("Payload", payload)

  const { isClockwise } = payload

  let newState = { ...state }
  newState.nextTile =  { ...state.nextTile }
  const rot = newState.nextTile.rot + 90 * (isClockwise ? -1 : 1)
  newState.nextTile.rot = (rot + 360) % 360

  console.log("New State", newState)
  return newState
}