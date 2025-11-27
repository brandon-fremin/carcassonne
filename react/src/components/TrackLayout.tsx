import { useEffect, useRef, useState } from 'react'

// 🎨 Colors for track/accessory types
const typeColors: string[] = [
  "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
  "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
];

// 🧱 Type definitions
interface Track {
  Z_PK: number;
  ZTRACKLOCATIONX: number;
  ZTRACKLOCATIONY: number;
  ZTRACKORIENTATION?: number;
  ZTRACKTYPE: number;
  ZTRACKPAGE: number;
  [key: string]: any;
}

interface Accessory {
  Z_PK: number;
  ZACCLOCATIONX: number;
  ZACCLOCATIONY: number;
  ZACCPAGE: number;
  ZACCTYPEID: number;
  [key: string]: any;
}

interface Page {
  Z_PK: number;
  ZPAGENAME: string;
  [key: string]: any;
}

interface Tooltip {
  x: number;
  y: number;
  data: any;
}

// 🧾 Recursive JSON viewer
const JSONViewer: React.FC<{ data: any; indent?: number }> = ({ data, indent = 0 }) => {
  if (typeof data !== "object" || data === null) {
    return <span>{String(data)}</span>;
  }

  return (
    <div style={{ display: "block", textAlign: "left", paddingLeft: indent * 16 }}>
      {Object.entries(data).map(([key, value]) => (
        <div key={key} style={{ display: "block", textAlign: "left" }}>
          <span style={{ color: "#333" }}>
            <strong>{key}</strong>:{" "}
          </span>
          {typeof value === "object" && value !== null ? (
            <JSONViewer data={value} indent={indent + 1} />
          ) : (
            <span style={{ color: "#555" }}>{String(value)}</span>
          )}
        </div>
      ))}
    </div>
  );
};

function stripSvgWrapper(svgString: string): string {
  const match = svgString.match(/<svg[^>]*>([\s\S]*?)<\/svg>/i);
  return match ? match[1] : `<circle r="10" />`; // fallback if no match
}

function parseViewBox(svgString: string) {
  const match = svgString.match(/viewBox="([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)"/i);
  if (!match) return { minX: 0, minY: 0, width: 0, height: 0 }; // default fallback

  const [_, minX, minY, width, height] = match.map(Number);
  return { minX, minY, width, height };
}

const TrackLayout: React.FC = () => {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [accessories, setAccessories] = useState<Accessory[]>([]);
  const [pages, setPages] = useState<Page[]>([]);
  const [selectedPage, setSelectedPage] = useState<number | null>(null);
  const [tooltip, setTooltip] = useState<Tooltip | null>(null);
  const [svgMap, setSvgMap] = useState<Record<number, string | null> | null>(null);
  const containerRef = useRef<SVGSVGElement>(null);

  // 🪄 Fetch data once
  useEffect(() => {
    fetch("https://react.brandonfremin.com/api/lionel")
      .then((res) => res.json())
      .then((json) => {
        setTracks(json.ZTRACKDATA || []);
        setAccessories(json.ZACCDATA || []);
        setPages(json.ZPAGEDATA || []);
        setSvgMap(json.svg || null);
        if (json.ZPAGEDATA?.length > 0) setSelectedPage(json.ZPAGEDATA[0].Z_PK);
      })
      .catch((err) => console.error("Error fetching Lionel data:", err));
  }, []);

  // 🧭 Hover tooltips
  const handleMouseEnter = (
    e: React.MouseEvent<SVGElement>,
    data: Track | Accessory
  ) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setTooltip({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      data,
    });
  };

  console.log(tooltip)

  const handleMouseLeave = () => setTooltip(null);

  // 🎚 Filter by selected page (Z_PK)
  const filteredTracks = selectedPage
    ? tracks.filter((t) => t.ZTRACKPAGE === selectedPage)
    : tracks;

  const filteredAccessories = selectedPage
    ? accessories.filter((a) => a.ZACCPAGE === selectedPage)
    : accessories;

  // 🧮 Adjustable layout box size
  const xs = filteredTracks.map(t => t.ZTRACKLOCATIONX)
  const ys = filteredTracks.map(t => t.ZTRACKLOCATIONY)
  const boxWidth = (Math.max(...xs) - Math.min(...xs)) * 2;
  const boxHeight = (Math.max(...ys) - Math.min(...ys)) * 2;
  const avgX = (Math.min(...xs) + Math.max(...xs)) / 2
  const avgY = (Math.min(...ys) + Math.max(...ys)) / 2
  const xOffset = boxWidth / 2 - avgX;
  const yOffset = boxHeight / 2 - avgY;

  const PageSelector = () => {
    return (
      <div style={{ marginBottom: 12 }}>
        <label htmlFor="pageSelect">Select Page: </label>
        <select
          id="pageSelect"
          value={selectedPage ?? ""}
          onChange={(e) => setSelectedPage(Number(e.target.value))}
        >
          {pages.map((p) => (
            <option key={p.Z_PK} value={p.Z_PK}>
              {p.ZPAGENAME || `Page ${p.Z_PK}`}
            </option>
          ))}
        </select>
      </div>
    )
  }

  return (
    <div>
      <h2>Lionel Layout Viewer</h2>

      {/* Page selector */}
      <PageSelector />

      <svg
        ref={containerRef}
        style={{
          position: "relative",
          width: boxWidth,
          height: boxHeight,
          border: "1px solid #aaa",
          overflow: "auto",
          background: "#f8f8f8",
        }}
      >
        {filteredTracks.map((track) => {
          return <circle cx={xOffset + track.ZTRACKLOCATIONX} cy={yOffset + track.ZTRACKLOCATIONY} r="5" fill="pink" />
        })}
        {filteredTracks.map((track) => {
          const x = track.ZTRACKLOCATIONX;
          const y = track.ZTRACKLOCATIONY;
          const rotation = track.ZTRACKORIENTATION || 0;
          const color = typeColors[track.ZTRACKTYPE % typeColors.length];
          const svgStr = svgMap?.[track.ZTRACKTYPE] || ""
          const { minX, minY, width, height } = parseViewBox(svgStr)

          return (
            <g
              key={`track-${track.Z_PK}`}
              style={{pointerEvents: "all"}}
              // transform={`translate(${xOffset + x} ${yOffset + y}) scale(0.5) rotate(${rotation}) translate(${width/2 - minX} ${height/2 - minY})`}
              // transform={`translate(${xOffset + x - minX}, ${yOffset + y - minY}) scale(0.25)`}
              transform={`translate(${xOffset + x} ${yOffset + y}) scale(0.3) rotate(${rotation}) translate(${- width / 2 - minX} ${- height / 2 - minY})`}
              // onMouseEnter={(e) => handleMouseEnter(e, track)}
              // onMouseLeave={handleMouseLeave}
              dangerouslySetInnerHTML={{ __html: stripSvgWrapper(svgStr) }}
            />
          );
        })}
      </svg>

      {tooltip && (
        <div
          style={{
            position: "absolute",
            left: tooltip.x + 12,
            top: tooltip.y + 12,
            background: "#fff",
            padding: "10px 12px",
            border: "1px solid #aaa",
            borderRadius: 6,
            fontFamily: "Menlo, Consolas, monospace",
            fontSize: 12,
            color: "#111",
            maxWidth: 380,
            maxHeight: 400,
            overflow: "auto",
            boxShadow: "0 2px 10px rgba(0,0,0,0.25)",
            whiteSpace: "pre",
            textAlign: "left",
            lineHeight: 1.4,
            pointerEvents: "none",
            zIndex: 1000,
          }}
        >
          <JSONViewer data={tooltip.data} />
        </div>
      )}
    </div>
  );

  {/* Main layout container */ }
  <div
    ref={containerRef}
    style={{
      position: "relative",
      width: boxWidth,
      height: boxHeight,
      border: "1px solid #aaa",
      overflow: "auto",
      background: "#f8f8f8",
    }}
  >
    {/* 🟦 Tracks */}
    {filteredTracks.map((track) => {
      const x = track.ZTRACKLOCATIONX;
      const y = track.ZTRACKLOCATIONY;
      const rotation = track.ZTRACKORIENTATION || 0;
      const color = typeColors[track.ZTRACKTYPE % typeColors.length];

      return (
        <svg
          key={`track-${track.Z_PK}`}
          style={{
            position: "absolute",
            left: xOffset + x,
            top: yOffset + y,
            // width: 40,
            // height: 20,
            backgroundColor: color,
            transform: `rotate(${rotation}deg) scale(0.25)`,
            transformOrigin: "center center",
            border: "1px solid #000",
            cursor: "pointer",
          }}
          onMouseEnter={(e) => handleMouseEnter(e, track)}
          onMouseLeave={handleMouseLeave}
          dangerouslySetInnerHTML={{ __html: svgMap?.[track.ZTRACKTYPE] || "" }}
        />
      );
    })}

    {/* ⚪ Accessories */}
    {filteredAccessories.map((acc) => {
      const x = acc.ZACCLOCATIONX;
      const y = acc.ZACCLOCATIONY;
      const color = typeColors[acc.ZACCTYPEID % typeColors.length];

      return (
        <div
          key={`acc-${acc.Z_PK}`}
          style={{
            position: "absolute",
            left: xOffset + x - 6,
            top: yOffset + y - 6,
            width: 12,
            height: 12,
            borderRadius: "50%",
            backgroundColor: color,
            border: "1px solid #000",
            cursor: "pointer",
          }}
          onMouseEnter={(e) => handleMouseEnter(e, acc)}
          onMouseLeave={handleMouseLeave}
        />
      );
    })}

    {/* 🪶 Tooltip */}
    {tooltip && (
      <div
        style={{
          position: "absolute",
          left: tooltip.x + 12,
          top: tooltip.y + 12,
          background: "#fff",
          padding: "10px 12px",
          border: "1px solid #aaa",
          borderRadius: 6,
          fontFamily: "Menlo, Consolas, monospace",
          fontSize: 12,
          color: "#111",
          maxWidth: 380,
          maxHeight: 400,
          overflow: "auto",
          boxShadow: "0 2px 10px rgba(0,0,0,0.25)",
          whiteSpace: "pre",
          textAlign: "left",
          lineHeight: 1.4,
          pointerEvents: "none",
          zIndex: 1000,
        }}
      >
        <JSONViewer data={tooltip.data} />
      </div>
    )}
  </div>
};

export default TrackLayout;
