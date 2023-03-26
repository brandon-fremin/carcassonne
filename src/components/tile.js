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

function getTileContent(className, image, edge, rotation) {
  return (
    <div
      className={className}
      style={{
        height: TILE_SIDE, 
        width: TILE_SIDE,
        backgroundImage: `url(${image})`,
        backgroundSize: "cover",
        ...edge
      }}
    />
  )
}

function getTileOverlay(className, overlayEdge) {
  const side = ![TILE_CLASS.PREVIEW, TILE_CLASS.FULL].includes(className) ?
    "0px" : TILE_SIDE
  const topLeft = `${side === TILE_SIDE ? 0 : TILE_SIDE_INT / 2}px`

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

  return (
    <div
      className="tile-overlay"
      style={{
        height: side, 
        width: side,
        top: topLeft,
        left: topLeft,
        ...overlayEdge
      }}
    />
  )
}

export default function Tile({className, image, handleClick, rotation, tip, edge, overlayEdge}) {
  const tile = getTileContent(className, image, edge, rotation)
  const overlay = getTileOverlay(className, overlayEdge)
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