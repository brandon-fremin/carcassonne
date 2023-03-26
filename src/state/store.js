import { createStore, applyMiddleware } from "redux";
import thunk from "redux-thunk"
import globalStateReducer from "./reducer"

const INITIAL_STATE = {
  numRows: 1,
  numCols: 1,
  board: [],
  legalMoves: [],
  nextTile: undefined
}

const REDUX_STORE = createStore(
  globalStateReducer,
  INITIAL_STATE,
  applyMiddleware(thunk)
)

export default REDUX_STORE