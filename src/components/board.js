import { useSelector, useDispatch } from 'react-redux'
import { ACTIONS } from '../state/reducer'
import Tile, { TILE_CLASS, TILE_EDGE, TILE_SIDE_INT } from './tile'
import "./board.css"
import IMAGE_MAP from '../assets/tiles/tileimages'

function range(n, start=0) {
  if (n < 0) {
    return []
  }
  return [...Array(n).keys()].map(x => x + start)
}

function getRowRange(board) {
  let [min, max] = [0, 0]
  for (const tile of board) { 
    min = Math.min(min, tile.j)
    max = Math.max(max, tile.j)
  }
  const n = max - min + 3
  const start = min - 1
  return range(n, start).reverse()
}

function getColumnRange(board) {
  let [min, max] = [0, 0]
  for (const tile of board) { 
    min = Math.min(min, tile.i)
    max = Math.max(max, tile.i)
  }
  const n = max - min + 3
  const start = min - 1
  return range(n, start)
}

function getTileClassName(board, nextTile, i, j) {
  if (nextTile?.i === i && nextTile?.j === j) {
    return TILE_CLASS.PREVIEW
  }

  if (board.some((tile) => tile.i === i && tile.j === j)) {
    return TILE_CLASS.FULL
  }

  if (board.some((tile) => Math.abs(tile.i - i) + Math.abs(tile.j - j)  === 1)) {
    return TILE_CLASS.ADJACENT
  }
  
  return TILE_CLASS.EMPTY
}

function getTileImage(board, nextTile, i, j, className) {
  if (className === TILE_CLASS.PREVIEW) {
    return IMAGE_MAP[nextTile.image]
  }

  for (const tile of board) { 
    if (tile.i === i && tile.j === j) {
      return IMAGE_MAP[tile.image]
    } 
  } 
}

function getTileEdge(legalMoves, nextTile, i, j, className) {
  if (!legalMoves || ! nextTile) {
    return className === TILE_EDGE.DEFAULT
  }
  const rot = nextTile.rot

  // check if we have an exact match
  if (legalMoves.some((move) => 
    move.i === i && move.j === j && move.rot === rot
  )) {
    return TILE_EDGE.LEGAL
  }

  // check if we are off by rotation
  if (legalMoves.some((move) => 
    move.i === i && move.j === j
  )) {
    return TILE_EDGE.ROTATE
  }

  return TILE_EDGE.DEFAULT
}

function getTileOverlayEdge(legalMoves, nextTile, i, j, className) {
  if ([TILE_CLASS.EMPTY, TILE_CLASS.FULL, TILE_CLASS.ADJACENT].includes(className)) {
    return undefined
  } 
  const edge = getTileEdge(legalMoves, nextTile, i, j, className)
  return [TILE_EDGE.ILLEGAL, TILE_EDGE.ROTATE, TILE_EDGE.DEFAULT].includes(edge) ? TILE_EDGE.ILLEGAL : undefined
}

function getTileTip(legalMoves, nextTile, i, j, className) {
  const edge = getTileEdge(legalMoves, nextTile, i, j, className)
  if ([TILE_CLASS.EMPTY, TILE_CLASS.FULL].includes(className)) {
    return ""
  }
  if (edge === TILE_EDGE.LEGAL) {
    return "Click to preview tile placement :)"
  } else if (edge === TILE_EDGE.ROTATE) {
    return "Rotate tile to place here!"
  } else {
    return "Can't place tile here :("
  }
}

function getTileHandleClick(i, j, className, dispatch) {
  if (className !== TILE_CLASS.ADJACENT) {
    return undefined
  }

  const handleClick = () => {
    dispatch({
      type: ACTIONS.PREVIEW_PLACEMENT,
      payload: { i, j }
    })
  }
  return handleClick
}

function getTileRotation(board, nextTile, i, j, className) {
  if (className === TILE_CLASS.PREVIEW) {
    return nextTile.rot
  }
  for (const tile of board) { 
    if (tile.i === i && tile.j === j) {
      return tile.rot
    } 
  }
}

function Row({j, board, nextTile, legalMoves}) {
  const columnRange = getColumnRange(board)
  const dispatch = useDispatch()

  return (
    <div className="row" key={j}>
      {columnRange.map((i) => {
        const className = getTileClassName(board, nextTile, i, j)
        return (
          <Tile 
            key={i} 
            className   = {className}
            image       = {getTileImage(board, nextTile, i, j, className)}
            tip         = {getTileTip(legalMoves, nextTile, i, j, className)}
            edge        = {getTileEdge(legalMoves, nextTile, i, j, className)}
            overlayEdge = {getTileOverlayEdge(legalMoves, nextTile, i, j, className)}
            handleClick = {getTileHandleClick(i, j, className, dispatch)}
            rotation    = {getTileRotation(board, nextTile, i, j, className)}
          />
        )
      })}
    </div>
  )
}

export default function Board() {
  const board = useSelector((state) => state.board)
  const nextTile = useSelector((state) => state.nextTile)
  const legalMoves = useSelector((state) => state.legalMoves)
  const rowRange = getRowRange(board)
  const columnRange = getColumnRange(board)

  return (
    <div className="board-container"
      style={{
        minHeight: (rowRange.length + 1) * TILE_SIDE_INT,
        minWidth: (columnRange.length + 1) * TILE_SIDE_INT
      }}
    >
      <div className="board">
        {rowRange.map((j) => <Row key={j} j={j} board={board} nextTile={nextTile} legalMoves={legalMoves}/>)} 
      </div>
    </div>
  )
} 