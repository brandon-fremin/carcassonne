import "./TileList.css"

export const TILE_SIDE_INT = 100
export const TILE_SIDE = `${TILE_SIDE_INT}px`
const rot = 0
export const ROTATION = `-${rot || 0}deg`

const house = <svg fill="#000000">
    <path
        d="M 60.011 45.09 l 4.6538 4.7754 c 0.56231 0.58521 0.40184 1.0364 -0.36075 1.0364 h -3.4907 v 12.477 c 0 0.8562 -0.64191 1.6216 -1.4045 1.6216 h -6.0583 v -8.7392 c 0 -0.8562 -0.68171 -1.6216 -1.4443 -1.6216 h -3.8117 c -0.76259 0 -1.4443 0.76539 -1.4443 1.6216 v 8.7392 h -6.0583 c -0.76259 0 -1.4443 -0.76539 -1.4443 -1.6216 v -12.477 h -3.4509 c -0.76259 0 -0.92307 -0.45116 -0.36075 -1.0364 l 13.601 -13.874 c 0.56231 -0.58521 1.5252 -0.58521 2.126 0 l 3.0889 3.1077 v -2.4778 c 0 -0.8562 0.68171 -1.6216 1.4443 -1.6216 h 3.0093 c 0.76259 0 1.4045 0.76539 1.4045 1.6216 v 8.4683 z"
    />
</svg>

function StraightRoad() {
    return (
        <div
            className="tile"
            style={{
                "--tile-side": TILE_SIDE,
                "--rotation": ROTATION
            }}
        >
            <svg height={TILE_SIDE} width={TILE_SIDE}>
                <path
                    // Left Field
                    d="M 0 0 L 45 0 L 45 100 L 0 100 Z"
                    fill="green"
                    onClick={() => {console.log("StraightRoad - Left Field")}}
                />
                <path
                    // top-to-bottom road
                    d="M 45 0 L 45 100 L 55 100 L 55 0 Z"
                    fill="grey"
                    onClick={() => {console.log("StraightRoad - Road")}}
                />
                <path
                    // Right Field
                    d="M 55 0 L 55 100 L 100 100 L 100 0 Z"
                    fill="green"
                    onClick={() => {console.log("StraightRoad - Right Field")}}
                />
            </svg>
        </div>
    )
}

function CurvedRoad() {
    return (
        <div
            className="tile"
            style={{
                "--tile-side": TILE_SIDE,
                "--rotation": ROTATION
            }}
        >
            <svg height={TILE_SIDE} width={TILE_SIDE}>
                <path
                    // Road
                    d="M 0 45 A 55 55 0 0 1 55 100 L 45 100 A 45 45 0 0 0 0 55 Z"
                    fill="grey"
                    onClick={() => {console.log("CurvedRoad - Road")}}
                />
                <path
                    // Small Field
                    d="M 0 55 A 45 45 0 0 1 45 100 L 0 100 Z"
                    fill="green"
                    onClick={() => {console.log("CurvedRoad - Small Field")}}
                />
                <path
                    // Big Field
                    d="M 0 45 A 55 55 0 0 1 55 100 L 100 100 L 100 0 L 0 0 Z"
                    fill="green"
                    onClick={() => {console.log("CurvedRoad - Big Field")}}
                />
            </svg>
        </div>
    )
}

function BlockedCrossRoad() {
    return (
        <div
            className="tile"
            style={{
                "--tile-side": TILE_SIDE,
                "--rotation": ROTATION
            }}
        >
            <svg height={TILE_SIDE} width={TILE_SIDE}>
                <path
                    // Left Road
                    d="M 0 45 L 50 45 L 50 55 L 0 55 Z"
                    fill="grey"
                    onClick={() => {console.log("BlockedCrossRoad - Left Road")}}
                />
                <path
                    // Right Road
                    d="M 100 45 L 50 45 L 50 55 L 100 55 Z"
                    fill="grey"
                    onClick={() => {console.log("BlockedCrossRoad - Right Road")}}
                />
                <path
                    // Top Road
                    d="M 45 0 L 45 50 L 55 50 L 55 0 Z"
                    fill="grey"
                    onClick={() => {console.log("BlockedCrossRoad - Top Road")}}
                />
                <path
                    // Bottom Road
                    d="M 45 100 L 45 50 L 55 50 L 55 100 Z"
                    fill="grey"
                    onClick={() => {console.log("BlockedCrossRoad - Bottom Road")}}
                />
                <path
                    // Top Left Field 
                    d="M 0 0 L 0 45 L 45 45 L 45 0 Z"
                    fill="green"
                    onClick={() => {console.log("BlockedCrossRoad - Top Left Field")}}
                />
                <path
                    // Top Right Field 
                    d="M 55 0 L 55 45 L 100 45 L 100 0 Z"
                    fill="green"
                    onClick={() => {console.log("BlockedCrossRoad - Top Right Field")}}
                />
                <path
                    // Bottom Left Field 
                    d="M 0 55 L 45 55 L 45 100 L 0 100 Z"
                    fill="green"
                    onClick={() => {console.log("BlockedCrossRoad - Bottom Left Field")}}
                />
                <path
                    // Bottom Right Field 
                    d="M 55 55 L 100 55 L 100 100 L 55 100 Z"
                    fill="green"
                    onClick={() => {console.log("BlockedCrossRoad - Bottom Right Field")}}
                />
                <path
                    // Blocking
                    d="M 35 50 A 15 15 0 0 1 65 50 A 15 15 0 0 1 35 50 Z"
                    fill="brown"
                    onClick={() => {console.log("BlockedCrossRoad - Blocking")}}
                />
            </svg>
        </div>
    )
}

{/* <path
                    // M 0 0              --> move to 0,0
                    // L 100 0            --> line to 100,0
                    // A 50 25 0 0 1 0 0  --> arch <rx> <ry> 0 0 <clockwise> <x> <y>
                    d="M 0 0 L 100 0 A 200 200 0 0 0 0 100 Z"
                    stroke="blue" 
                    strokeWidth="2" 
                    fill="blue" 
                    fillOpacity="0.2" 
                /> */}

export default function TileList() {
    return (
        <div className="tile-list">
            <StraightRoad key={0} />
            <StraightRoad key={1} />
            <StraightRoad key={2} />
            <CurvedRoad key={3} />
            <BlockedCrossRoad key={4} />
        </div>
    )
}

<svg
    fill="#000000"
    viewBox="-4.5 0 32 32"
    version="1.1"
    xmlns="http://www.w3.org/2000/svg"
>
    <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
    <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
    <g id="SVGRepo_iconCarrier">
        <title>home</title>
        <path
            d="M19.469 12.594l3.625 3.313c0.438 0.406 0.313 0.719-0.281 0.719h-2.719v8.656c0 0.594-0.5 1.125-1.094 1.125h-4.719v-6.063c0-0.594-0.531-1.125-1.125-1.125h-2.969c-0.594 0-1.125 0.531-1.125 1.125v6.063h-4.719c-0.594 0-1.125-0.531-1.125-1.125v-8.656h-2.688c-0.594 0-0.719-0.313-0.281-0.719l10.594-9.625c0.438-0.406 1.188-0.406 1.656 0l2.406 2.156v-1.719c0-0.594 0.531-1.125 1.125-1.125h2.344c0.594 0 1.094 0.531 1.094 1.125v5.875z"
        >
        </path>
    </g></svg>