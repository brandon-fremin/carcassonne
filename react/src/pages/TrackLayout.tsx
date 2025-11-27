import { useState, useEffect } from 'react';
import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Button, TextField, Fab, IconButton } from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';

interface TrackResponse {
  centerlines: Array<{
    path: string;
    startAnchorId: string;
    endAnchorId: string;
  }>;
  ties: Array<{ path: string }>;
  rails: Array<{ path: string }>;
  anchors: Array<{
    id: string;
    tangent: string;
    normal: string;
  }>;
  boundingBox: {
    xmin: number;
    xmax: number;
    ymin: number;
    ymax: number;
  };
}

interface SavedTrack {
  id: string;
  name: string;
  data: TrackResponse;
}

interface Layout {
  id: string;
  name: string;
  tracks: Array<{
    trackId: string;
    position: { x: number; y: number };
    rotation: number;
  }>;
}

function TrackSvg(props: { data: TrackResponse; size: number }) {
  const { data, size } = props;
  
  if (!data || !data.boundingBox) {
    return <div style={{ width: size, height: size, backgroundColor: '#f0f0f0' }}></div>;
  }

  const { xmin, xmax, ymin, ymax } = data.boundingBox;
  const padding = 10;
  const x = xmin - padding;
  const y = ymin - padding;
  const width = (xmax - xmin) + (padding * 2);
  const height = (ymax - ymin) + (padding * 2);
  const viewBox = `${x} ${y} ${width} ${height}`;

  return (
    <svg width={size} height={size} viewBox={viewBox}>
      {/* Centerlines */}
      {data.centerlines.map((centerline, i) => (
        <path
          key={`centerline-${i}`}
          d={centerline.path}
          stroke="blue"
          strokeWidth="0.5"
          fill="none"
          opacity="0.5"
        />
      ))}

      {/* Ties */}
      {data.ties.map((tie, i) => (
        <path
          key={`tie-${i}`}
          d={tie.path}
          fill="brown"
          stroke="none"
        />
      ))}

      {/* Rails */}
      {data.rails.map((rail, i) => (
        <polygon
          key={`rail-${i}`}
          points={rail.path}
          fill="#404040"
          stroke="#202020"
          strokeWidth="0.2"
        />
      ))}

      {/* Anchors */}
      {data.anchors.map((anchor) => (
        <g key={anchor.id}>
          <path
            d={anchor.tangent}
            fill="red"
            stroke="darkred"
            strokeWidth="0.3"
          />
          <path
            d={anchor.normal}
            fill="green"
            stroke="darkgreen"
            strokeWidth="0.3"
          />
        </g>
      ))}
    </svg>
  );
}

export default function TrackLayout() {
  const [tracks, setTracks] = useState<SavedTrack[]>([]);
  const [layouts, setLayouts] = useState<Layout[]>([]);
  const [selectedLayoutId, setSelectedLayoutId] = useState<string>('');
  const [selectedLayout, setSelectedLayout] = useState<Layout | null>(null);
  const [newLayoutName, setNewLayoutName] = useState<string>('');
  const [isCreatingLayout, setIsCreatingLayout] = useState<boolean>(false);

  useEffect(() => {
    fetchTracks();
    fetchLayouts();
  }, []);

  const fetchTracks = async () => {
    try {
      const response = await fetch('https://react.brandonfremin.com/api/track');
      if (response.ok) {
        const data = await response.json();
        setTracks(data.tracks);
      }
    } catch (error) {
      console.error('Failed to fetch tracks:', error);
    }
  };

  const fetchLayouts = async () => {
    try {
      const response = await fetch('https://react.brandonfremin.com/api/layout');
      if (response.ok) {
        const data = await response.json();
        console.log(data)
        setLayouts(data.layouts || []);
        if (data.layouts && data.layouts.length > 0) {
          setSelectedLayoutId(data.layouts[0].id);
          setSelectedLayout(data.layouts[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch layouts:', error);
    }
  };

  const handleLayoutChange = (event: SelectChangeEvent) => {
    const layoutId = event.target.value;
    setSelectedLayoutId(layoutId);
    const layout = layouts.find(l => l.id === layoutId);
    setSelectedLayout(layout || null);
  };

  const handleCreateLayout = async () => {
    if (!newLayoutName.trim()) return;

    try {
      const response = await fetch('https://react.brandonfremin.com/api/layout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          layoutName: newLayoutName
        })
      });

      if (response.ok) {
        await response.json();
        setNewLayoutName('');
        setIsCreatingLayout(false);
        fetchLayouts();
      }
    } catch (error) {
      console.error('Failed to create layout:', error);
    }
  };

  const handleDeleteLayout = async (layoutId: string) => {
    try {
      const url = new URL('https://react.brandonfremin.com/api/layout');
      url.searchParams.set('id', layoutId);
      const response = await fetch(url.toString(), {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        fetchLayouts();
      }
    } catch (error) {
      console.error('Failed to delete layout:', error);
    }
  };

  return (
    <Box className="p-6 flex flex-col gap-4">
      <Box className="flex items-center justify-between">
        <Typography variant="h4" component="h1" className="font-bold">
          Layout Editor
        </Typography>
        <Fab color="primary" size="small" onClick={() => setIsCreatingLayout(true)}>
          <AddIcon />
        </Fab>
      </Box>

      {/* Create New Layout */}
      {isCreatingLayout && (
        <Box className="flex gap-2 items-center max-w-md">
          <TextField
            label="Layout Name"
            value={newLayoutName}
            onChange={(e) => setNewLayoutName(e.target.value)}
            size="small"
            className="flex-1"
          />
          <Button variant="contained" onClick={handleCreateLayout}>
            Create
          </Button>
          <Button variant="outlined" onClick={() => setIsCreatingLayout(false)}>
            Cancel
          </Button>
        </Box>
      )}

      {/* Layout Selection */}
      <Box className="flex gap-2 items-center max-w-md">
        <FormControl className="flex-1">
          <InputLabel>Select Layout</InputLabel>
          <Select
            value={selectedLayoutId}
            label="Select Layout"
            onChange={handleLayoutChange}
          >
            {layouts.map((layout) => (
              <MenuItem key={layout.id} value={layout.id}>
                {layout.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Layout Canvas */}
      {selectedLayout && (
        <Box>
          <Box className="flex items-center gap-2 mb-2">
            <Typography variant="h6" className="font-semibold">
              {selectedLayout.name}
            </Typography>
            <IconButton
              color="error"
              size="small"
              onClick={() => handleDeleteLayout(selectedLayout.id)}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Box>
          <Box className="border border-gray-300 bg-gray-50 p-4" style={{ minHeight: '600px' }}>
            <Typography variant="body2" color="text.secondary">
              Layout editor canvas - drag and drop tracks here
            </Typography>
            {/* TODO: Add interactive track placement */}
          </Box>
        </Box>
      )}

      {/* Available Tracks Palette */}
      <Box>
        <Typography variant="h6" className="font-semibold mb-2">
          Available Tracks
        </Typography>
        <Box className="flex gap-3 flex-wrap">
          {tracks.map((track) => (
            <Box
              key={track.id}
              className="border border-gray-300 bg-white p-2 cursor-pointer hover:border-blue-500"
              style={{ width: 120 }}
            >
              <Typography variant="caption" className="font-semibold block mb-1 truncate">
                {track.name}
              </Typography>
              <TrackSvg data={track.data} size={100} />
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
}