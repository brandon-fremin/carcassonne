import handleBoardResize from "./handlers/handleboardresize"
import handlePreviewPlacement from "./handlers/handlepreviewplacement";
import handleUpdateBoard from "./handlers/handleupdateboard";
import handleRotateNextTile from "./handlers/handlerotatenexttile";

export const ACTIONS = {
  BOARD_RESIZE: "BOARD_RESIZE",
  UPDATE_BOARD: "UPDATE_BOARD",
  PREVIEW_PLACEMENT: "PREVIEW_PLACEMENT",
  ROTATE_NEXT_TILE: "ROTATE_NEXT_TILE"
};

//Reducer to Handle Actions
const globalStateReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.BOARD_RESIZE:
      return handleBoardResize(state, action.payload)
    case ACTIONS.UPDATE_BOARD:
      return handleUpdateBoard(state, action.payload)
    case ACTIONS.PREVIEW_PLACEMENT:
      return handlePreviewPlacement(state, action.payload)
      case ACTIONS.ROTATE_NEXT_TILE:
        return handleRotateNextTile(state, action.payload)
    default: {
      console.log(`Unknown action: '${action.type}'`)
      return state
    }
  }
};

export default globalStateReducer