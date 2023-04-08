import { useDispatch, useSelector } from 'react-redux';
import React, {useState} from 'react'
import { ACTIONS } from '../state/reducer'
import Tile, { TILE_CLASS } from './tile';
import IMAGE_MAP from '../assets/tiles/tileimages';

function request(data={}) {
  return {
    method: "PUT",
    headers: { 'Content-Type': 'application/json' }, 
    body: JSON.stringify(data)
  }
}

export default function Interaction() {
  const dispatch = useDispatch();

  const sessionId = useSelector((state) => state.sessionId)
  const [sid, setSid] = useState(sessionId ? sessionId : '')
  const settings = useSelector((state) => state.defaultGameSettings)
  const nextTile = useSelector((state) => state.nextTile)
  const legalMoves = useSelector((state) => state.legalMoves)

  const handleInputChange = (event) => {
    setSid(event.target.value);
  };

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

  const getGameSettings = () => {
    fetch("/getGameSettings", request())
      .then(async (res) => {
        const response = await res.json()
        console.log(response)
        dispatch({
          type: ACTIONS.DEFAULT_GAME_SETTINGS,
          payload: response
        })
      })
  }
  
  const getGame = () => {
    fetch("/getGame", request({sessionId: sid})
    ).then(async (res) => {
      const response = await res.json()
      console.log(response)
      dispatch({
        type: ACTIONS.SET_GAME,
        payload: response
      })
    })
  }

  const newGame = () => {
    fetch("/newGame", request({settings: settings})).then(async (res) => {
      const response = await res.json()
      console.log(response)
      dispatch({
        type: ACTIONS.SET_SESSION_ID,
        payload: response
      })
      setSid(response.sessionId)
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
       <button onClick={getGameSettings}>
        Get Game Settings
      </button>
      <div style={{display: "flex"}}>
        <button  onClick={newGame}>
          New Game
        </button>
        <div>
          {sessionId}
        </div>
      </div>
      <div style={{display: "flex"}}>
        <button onClick={getGame}>
          Get Game
        </button>
        <input
          value={sid}
          onChange={handleInputChange}
        />
      </div>
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