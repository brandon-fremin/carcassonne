import { useDispatch, useSelector } from 'react-redux';
import { ACTIONS } from '../state/reducer'
import Tile, { TILE_CLASS } from './tile';
import IMAGE_MAP from '../assets/tiles/tileimages';

export default function Interaction() {
  const dispatch = useDispatch();

  const nextTile = useSelector((state) => state.nextTile)
  const legalMoves = useSelector((state) => state.legalMoves)

  const handleClick = () => {
    dispatch({
      type: ACTIONS.PREVIEW_PLACEMENT,
      payload: { i: null, j: null }
    })
  }

  const rotateCCW = () => {
    dispatch({
      type: ACTIONS.ROTATE_NEXT_TILE,
      payload: { isClockwise: false }
    })
  }

  const rotateCW = () => {
    dispatch({
      type: ACTIONS.ROTATE_NEXT_TILE,
      payload: { isClockwise: true }
    })
  }
  
  const nextTileDiv = !nextTile ?
    <Tile className={TILE_CLASS.ADJACENT} /> :
    nextTile.i === null ?
    <Tile className={TILE_CLASS.FULL} rotation={nextTile?.rot} image={IMAGE_MAP[nextTile?.image]}/> :
    <Tile className={TILE_CLASS.ADJACENT} handleClick={handleClick}/>
  
  const fetchBoard = () => {
    fetch("/getState", 
      {
        method: "PUT",
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({})
      }
    ).then(async (res) => {
      const response = await res.json()
      console.log(response)
      dispatch({
        type: ACTIONS.UPDATE_BOARD,
        payload: response
      })
    })
  }

  const newGame = () => {
    fetch("/newGame", 
      {
        method: "PUT",
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({})
      }
    ).then(async (res) => {
      const response = await res.json()
      console.log(response)
    })
  }

  const placeTileDisabled = !legalMoves.some((move) => 
    move.i === nextTile.i && move.j === nextTile.j && move.rot === nextTile.rot
  )
  const placeTile = () => {
    fetch("/placeTile", 
      {
        method: "PUT",
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({
          i: nextTile.i,
          j: nextTile.j,
          rot: nextTile.rot
        })
      }
    ).then(async (res) => {
      const response = await res.json()
      console.log(response)
      dispatch({
        type: ACTIONS.UPDATE_BOARD,
        payload: response
      })
    })
  }

  return (
    <div style={{display: "flex", flexDirection: "column", alignItems: "center", gap: "5px"}}>
      <button onClick={newGame}>
        New Game
      </button>
      <button onClick={fetchBoard}>
        Fetch Board
      </button>
      {nextTileDiv}
      <div style={{display: "flex", flexDirection: "row", gap: "10px"}}>
        <button onClick={rotateCW}>CW</button>
        <button onClick={rotateCCW}>CCW</button>
      </div>
      <button onClick={placeTile} disabled={placeTileDisabled}>
        Place Tile
      </button>
    </div>
  )
}