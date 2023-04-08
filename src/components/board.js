import { useSelector, useDispatch } from 'react-redux'
import { ACTIONS } from '../state/reducer'
import Tile, { TILE_CLASS, TILE_EDGE, TILE_SIDE_INT } from './tile'
import "./board.css"
import IMAGE_MAP from '../assets/tiles/tileimages'

function range(n, start = 0) {
  if (n < 0) {
    return []
  }
  return [...Array(n).keys()].map(x => x + start)
}

function getRowRange(board) {
  let [min, max] = [0, 0]
  for (const tile of Object.values(board.tiles)) {
    min = Math.min(min, tile.transform.j)
    max = Math.max(max, tile.transform.j)
  }
  const n = max - min + 3
  const start = min - 1
  return range(n, start).reverse()
}

function getColumnRange(board) {
  let [min, max] = [0, 0]
  for (const tile of Object.values(board.tiles)) {
    min = Math.min(min, tile.transform.i)
    max = Math.max(max, tile.transform.i)
  }
  const n = max - min + 3
  const start = min - 1
  return range(n, start)
}

function getTileClassName(board, nextTile, i, j) {
  if (nextTile.transform.i === i && nextTile.transform.j === j) {
    return TILE_CLASS.PREVIEW
  }

  if (Object.values(board.tiles).some(
    (tile) => tile.transform.i === i && tile.transform.j === j)
  ) {
    return TILE_CLASS.FULL
  }

  if (Object.values(board.tiles).some(
    (tile) => Math.abs(tile.transform.i - i) + Math.abs(tile.transform.j - j) === 1)
  ) {
    return TILE_CLASS.ADJACENT
  }

  return TILE_CLASS.EMPTY
}

function getTileImage(board, nextTile, i, j, className) {
  if (className === TILE_CLASS.PREVIEW) {
    return IMAGE_MAP[nextTile.image]
  }

  for (const tile of Object.values(board.tiles)) {
    if (tile.transform.i === i && tile.transform.j === j) {
      return IMAGE_MAP[tile.image]
    }
  }
}

function getTileEdge(legalMoves, nextTile, i, j, className) {
  if (!legalMoves || !nextTile || className === TILE_CLASS.FULL || className == TILE_CLASS.EMPTY) {
    return TILE_EDGE.DEFAULT
  }
  const rot = nextTile.transform.rot

  // check if we have an exact match
  if (legalMoves.some((move) =>
    move.transform.i === i && move.transform.j === j && move.transform.rot === rot
  )) {
    return TILE_EDGE.LEGAL
  }

  // check if we are off by rotation
  if (legalMoves.some((move) =>
    move.transform.i === i && move.transform.j === j
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
    return nextTile.transform.rot
  }
  for (const tile of Object.values(board.tiles)) {
    if (tile.transform.i === i && tile.transform.j === j) {
      return tile.transform.rot
    }
  }
}

function Row({ j, board, nextTile, legalMoves }) {
  const columnRange = getColumnRange(board)
  const dispatch = useDispatch()

  return (
    <div className="row" key={j}>
      {columnRange.map((i) => {
        const className = getTileClassName(board, nextTile, i, j)
        return (
          <Tile
            key={i}
            className={className}
            image={getTileImage(board, nextTile, i, j, className)}
            tip={getTileTip(legalMoves, nextTile, i, j, className)}
            edge={getTileEdge(legalMoves, nextTile, i, j, className)}
            overlayEdge={getTileOverlayEdge(legalMoves, nextTile, i, j, className)}
            handleClick={getTileHandleClick(i, j, className, dispatch)}
            rotation={getTileRotation(board, nextTile, i, j, className)}
          />
        )
      })}
    </div>
  )
}

export default function Board() {
  const board = useSelector((state) => state?.game?.board)
  const nextTile = useSelector((state) => state?.game?.board?.nextTile)
  const legalMoves = useSelector((state) => state?.game?.board?.legalMoves)

  if (!board) {
    return (
      <div className="board-container">
        No Board To Render
      </div>
    )
  }

  const rowRange = getRowRange(board)
  const columnRange = getColumnRange(board)

  console.log(board)

  return (
    <div className="board-container"
      style={{
        minHeight: (rowRange.length + 1) * TILE_SIDE_INT,
        minWidth: (columnRange.length + 1) * TILE_SIDE_INT
      }}
    >
      <div className="board">
        {rowRange.map((j) => <Row key={j} j={j} board={board} nextTile={nextTile} legalMoves={legalMoves} />)}
      </div>
    </div>
  )
} 