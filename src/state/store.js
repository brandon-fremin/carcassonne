import { createStore, applyMiddleware } from "redux";
import thunk from "redux-thunk"
import globalStateReducer from "./reducer"

const INITIAL_STATE = {
  version: 0
}

const REDUX_STORE = createStore(
  globalStateReducer,
  INITIAL_STATE,
  applyMiddleware(thunk)
)

export default REDUX_STORE