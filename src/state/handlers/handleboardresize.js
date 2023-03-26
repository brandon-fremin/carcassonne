export default function handleBoardResize(state, payload) {
  console.log("Old State", state)
  console.log("Payload", payload)

  let newState = {...state}
  const {isRow, delta} = payload
  if (isRow) {
    newState.numRows += delta
  } else {
    newState.numCols += delta
  }

  console.log("New State", newState)
  return newState
}

