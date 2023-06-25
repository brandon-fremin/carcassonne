import { useSelector, useDispatch } from 'react-redux'
import { ACTIONS } from '../state/reducer'
import Tile, { TILE_CLASS, TILE_EDGE, TILE_SHADE, TILE_SIDE_INT } from './tile'
import "./board.css"
import IMAGE_MAP from '../assets/tiles/tileimages'

function range(n, start = 0) {
  if (n < 0) {
    return []
  }
  return [...Array(n).keys()].map(x => x + start)
}

class BoardData {
  constructor(dispatch, board, selectedComponentId) {
    this.dispatch = dispatch
    this.board = board;
    this.selectedComponentId = selectedComponentId;
  }

  getBoard() {
    return this.board
  }

  getTiles() {
    return this.board.tiles
  }

  getNextTile() {
    return this.board.nextTile
  }

  getLegalMoves() {
    return this.board.legalMoves
  }

  getSelectedComponent() {
    return this.board.components[this.selectedComponentId]
  }

  isLegal(i, j, rot) {
    const legalMoves = this.getLegalMoves()
    return legalMoves.some((move) =>
      move.transform.i === i && 
      move.transform.j === j && 
      move.transform.rot === rot)
  }

  isLegalNextTile() {
    const transform = this.getNextTile().transform
    return this.isLegal(transform.i, transform.j, transform.rot)
  }

  static tileAt(tile, i, j) {
    return (
      tile.transform.i === i &&
      tile.transform.j === j
    )
  }

  static tileBy(tile, i, j) {
    return (
      Math.abs(tile.transform.i - i) + Math.abs(tile.transform.j - j) === 1
    )
  }

  getRowRange() {
    let [min, max] = [0, 0]
    for (const tile of Object.values(this.getTiles())) {
      min = Math.min(min, tile.transform.j)
      max = Math.max(max, tile.transform.j)
    }
    const n = max - min + 3
    const start = min - 1
    return range(n, start).reverse()
  }

  getColumnRange() {
    let [min, max] = [0, 0]
    for (const tile of Object.values(this.getTiles())) {
      min = Math.min(min, tile.transform.i)
      max = Math.max(max, tile.transform.i)
    }
    const n = max - min + 3
    const start = min - 1
    return range(n, start)
  }

  tileClassName(i, j) {
    const nextTile = this.getNextTile()
    const tiles = this.getTiles()
    if (BoardData.tileAt(nextTile, i, j)) {
      return TILE_CLASS.PREVIEW
    }
    if (Object.values(tiles).some((tile) => BoardData.tileAt(tile, i, j))) {
      return TILE_CLASS.FULL
    }
    if (Object.values(tiles).some((tile) => BoardData.tileBy(tile, i, j))) {
      return TILE_CLASS.ADJACENT
    }
    return TILE_CLASS.EMPTY
  }

  tileImage(i, j) {
    const nextTile = this.getNextTile()
    const board = this.getBoard()
    if (this.tileClassName(i, j) === TILE_CLASS.PREVIEW) {
      return IMAGE_MAP[nextTile.image]
    }
    for (const tile of Object.values(board.tiles)) {
      if (BoardData.tileAt(tile, i, j)) {
        return IMAGE_MAP[tile.image]
      }
    }
  }

  tileEdge(i, j) {
    const className = this.tileClassName(i, j)
    const legalMoves = this.getLegalMoves()
    const nextTile = this.getNextTile()
    if (className === undefined) {
      console.error("Error!!!", this.board)
      return TILE_EDGE.NONE
    }

    if (className === TILE_CLASS.PREVIEW) {
      return this.isLegalNextTile() ? TILE_EDGE.LEGAL : TILE_EDGE.ILLEGAL
    }

    if (className === TILE_CLASS.ADJACENT) {
      // check if we have an exact match
      if (this.isLegal(i, j, nextTile.transform.rot)) {
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
    
    // EMPTY and FULL
    return TILE_EDGE.NONE
  }

  tileShade(i, j) {
    const comp = this.getSelectedComponent()
    if (
      this.tileClassName(i, j) === TILE_CLASS.FULL &&
      comp !== undefined &&
      comp.includedTileIds.includes(this.tileId(i, j))
    ) {
      if (comp.type === "Field") {
        return TILE_SHADE.GREEN
      } else if (comp.type === "Road") {
        return TILE_SHADE.BLUE
      } else if (comp.type === "City") {
        return TILE_SHADE.ORANGE
      } else if (comp.type === "Monastary") {
        return TILE_SHADE.PURPLE
      }
    }

    return TILE_SHADE.NONE
  }

  tileId(i, j) {
    const key = `[${i}, ${j}]`
    return this.board.frontier.tileIds[key]
  }

  tileData(i, j) {
    return this.board.tiles[this.tileId(i, j)]
  }

  tileTip(i, j) {
    const edge = this.tileEdge(i, j)
    const className = this.tileClassName(i, j)
    if (TILE_CLASS.EMPTY === className) {
      return ""
    } else if (TILE_CLASS.FULL === className) {
      const id = this.tileId(i, j)
      const rot = this.tileData(i, j).transform.rot
      return `${id} ${rot}ccw`
    }

    if (edge === TILE_EDGE.LEGAL) {
      return "Click to preview tile placement :)"
    } else if (edge === TILE_EDGE.ROTATE) {
      return "Rotate tile to place here!"
    } else {
      return "Can't place tile here :("
    }
  }

  tileHandleClick(i, j) {
    const className = this.tileClassName(i, j)
    if (className !== TILE_CLASS.ADJACENT) {
      return undefined
    }
    const handleClick = () => {
      this.dispatch({
        type: ACTIONS.PREVIEW_PLACEMENT,
        payload: { i, j }
      })
    }
    return handleClick
  }

  tileRotation(i, j) {
    const className = this.tileClassName(i, j)
    const nextTile = this.getNextTile()
    const board = this.getBoard()
    if (className === TILE_CLASS.PREVIEW) {
      return nextTile.transform.rot
    }
    for (const tile of Object.values(board.tiles)) {
      if (BoardData.tileAt(tile, i, j)) {
        return tile.transform.rot
      }
    }
  }

  tileClickables(i, j) {
    if (this.tileClassName(i, j) === TILE_CLASS.PREVIEW) {
      const nextTile = this.getNextTile()
      return nextTile.features.map((feature) => {
        const onClick = () => {
          console.log(feature.id, nextTile.id)
        }
        return {
          x: feature.clickable.x,
          y: feature.clickable.y,
          image: feature.image,
          onClick: onClick
        }
      })
    }
    return []
  }

  tile(i, j) {
    return (
      <Tile
        key={i}
        className={this.tileClassName(i, j)}
        image={this.tileImage(i, j)}
        tip={this.tileTip(i, j)}
        edge={this.tileEdge(i, j)}
        handleClick={this.tileHandleClick(i, j)}
        rotation={this.tileRotation(i, j)}
        shade={this.tileShade(i, j)}
        clickables={this.tileClickables(i, j)}
      />
    )
  }

  row(j) {
    return (
      <div className="row" key={j}>
        {this.getColumnRange().map((i) => this.tile(i, j))}
      </div>
    )
  }

  div() {
    const rowRange = this.getRowRange()
    const columnRange = this.getColumnRange()
    return (
      <div className="board-container"
        style={{
          minHeight: (rowRange.length + 1) * TILE_SIDE_INT,
          minWidth: (columnRange.length + 1) * TILE_SIDE_INT
        }}
      >
        <div className="board">
          {rowRange.map((j) => this.row(j))}
        </div>
      </div>
    )
  }
}

export default function Board() {
  const dispatch = useDispatch()
  const board = useSelector((state) => state?.game?.board)
  const selectedComponentId = useSelector((state) => state?.selectedComponentId)
  const _ = useSelector((state) => state?.game?.board?.nextTile)  // Monitor nextTile changes!

  if (board === undefined) {
    return (
      <div className="board-container">
        No Board To Render
      </div>
    )
  }

  const boardData = new BoardData(dispatch, board, selectedComponentId)
  return boardData.div()
} 