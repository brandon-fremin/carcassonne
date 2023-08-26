import "./tile.css"
import { Tooltip } from "@mui/material"

export const TILE_SIDE_INT = 100
export const TILE_SIDE = `${TILE_SIDE_INT}px`

export const TILE_CLASS = {
  FULL: "tile full",
  EMPTY: "tile empty",
  ADJACENT: "tile adjacent",
  PREVIEW: "tile preview"
}

export const TILE_EDGE = {
  NONE: undefined,
  LEGAL: {
    "--edge": "green"
  },
  ROTATE: {
    "--edge": "gold"
  },
  DEFAULT: {
    "--edge": "grey"
  },
  ILLEGAL: {
    "--edge": "red"
  }
}

export const TILE_SHADE = {
  NONE: undefined,
  BLUE: {
    "--overlay": "blue",
    "--opacity": 0.35
  },
  ORANGE: {
    "--overlay": "orange",
    "--opacity": 0.35
  },
  GREEN: {
    "--overlay": "green",
    "--opacity": 0.35
  },
  PURPLE: {
    "--overlay": "purple",
    "--opacity": 0.35
  }
}

function getTileContent(className, image) {
  return (
    <div
      className={className}
      style={{
        height: TILE_SIDE,
        width: TILE_SIDE,
        backgroundImage: `url(${image})`,
        backgroundSize: "cover"
      }}
    />
  )
}

function getTileOverlay(className, edge, shade, clickables) {
  // const side = ![TILE_CLASS.PREVIEW, TILE_CLASS.FULL].includes(className) ?
  //   "0px" : TILE_SIDE
  // const topLeft = `${side === TILE_SIDE ? 0 : TILE_SIDE_INT / 2}px`
  const side = TILE_SIDE
  const topLeft = 0  //TILE_SIDE_INT / 2

  clickables = []
  const svgs = clickables === undefined ? [] :
    clickables.map(({ x, y, image, onClick }) => {
      return (
        <circle
          key={`${x},${y}`}
          className="tile-clickable"
          cx={x} cy={100 - y} r="5"
          stroke="red"
          strokeWidth="2"
          fill="red"
          fillOpacity="0.6"
          onClick={onClick}
          cursor="pointer"
          style={{
            transition: "0.3s"
          }}
        />
      )
    })
  

  // return (
  //   <div className="tile-overlay">
  //     <svg width="100" height="100">
  //       {/* <circle 
  //         cx="50" cy="50" r="10" 
  //         stroke="red" 
  //         strokeWidth="2" 
  //         fill="red" 
  //         fillOpacity="0.6" 
  //         onClick={() => console.log("asdfasdf")}
  //         cursor="pointer"/>
  //       <polygon
  //         points="0,0 100,0 75,50 100,100 0,100 25,50"
  //         stroke="blue" 
  //         strokeWidth="2" 
  //         fill="blue" 
  //         fillOpacity="0.2" 
  //       /> */}
  //       <path
  //         // M 0 0              --> move to 0,0
  //         // L 100 0            --> line to 100,0
  //         // A 50 25 0 0 1 0 0  --> arch <rx> <ry> 0 0 <clockwise> <x> <y>
  //         d="M 0 0 L 100 0 A 50 25 0 0 1 0 0 Z"
  //         stroke="blue" 
  //         strokeWidth="2" 
  //         fill="blue" 
  //         fillOpacity="0.2" 
  //       />
  //       <path
  //         // M 0 0              --> move to 0,100
  //         // L 100 0            --> line to 100,100
  //         // A 50 25 0 0 1 0 0  --> arch <rx> <ry> 0 0 <clockwise> <x> <y>
  //         d="M 0 100 L 100 100 A 50 25 0 0 0 0 100 Z"
  //         stroke="blue" 
  //         strokeWidth="2" 
  //         fill="blue" 
  //         fillOpacity="0.2" 
  //       />
  //     </svg>
  //   </div>
  // )

  const hoverFill = className === TILE_CLASS.ADJACENT ?
    { "--hover-fill": "lightgrey" } : shade !== TILE_SHADE.NONE ?
      { "--hover-fill": shade["--overlay"] } : undefined

  return (
    <div
      className="tile-overlay"
      style={{
        height: side,
        width: side,
        top: topLeft,
        left: topLeft,
        ...edge,
        ...hoverFill,
        ...shade
      }}
    >
      <svg width="100" height="100" className="tile-clickable">
        {svgs}
      </svg>
    </div>
  )
}

export default function Tile({ className, image, handleClick, rotation, tip, edge, shade, clickables }) {
  const tile = getTileContent(className, image)
  const overlay = getTileOverlay(className, edge, shade, clickables)
  return (
    <Tooltip title={tip} placement={"top"}>
      <div
        className="tile-container"
        style={{
          height: TILE_SIDE,
          width: TILE_SIDE,
          cursor: handleClick ? "pointer" : undefined,
          transform: `rotate(-${rotation || 0}deg)`
        }}
        onClick={handleClick}
      >
        {tile}
        {overlay}
      </div>
    </Tooltip>
  )
}