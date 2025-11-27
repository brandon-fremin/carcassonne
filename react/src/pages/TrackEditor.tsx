import { useState, useEffect } from 'react';
import { Button, TextField, Box, Typography, Alert, FormControl, InputLabel, Select, MenuItem, FormControlLabel, Radio, RadioGroup, ToggleButtonGroup, ToggleButton, Card, CardContent, IconButton, Modal, Fab } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

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

function TrackSvg(props: { data: TrackResponse; size: number }) {
  const { data, size } = props;
  if (!data || !data.boundingBox) {
    console.log("Failed to render TrackSvg", size, data)
    return <div style={{ width: size, height: size, backgroundColor: 'pink' }}></div>;
  }

  const { xmin, xmax, ymin, ymax } = data.boundingBox;
  const padding = 10;
  const x = xmin - padding;
  const y = ymin - padding;
  const width = (xmax - xmin) + (padding * 2);
  const height = (ymax - ymin) + (padding * 2);
  const viewBox = `${x} ${y} ${width} ${height}`;

  return <svg width={size} height={size} viewBox={viewBox}>
    {/* <g transform="scale(1, -1)"> */}
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
    {/* </g> */}
  </svg>
}

export default function TrackEditor() {
  const [trackType, setTrackType] = useState<'straight' | 'arc' | 'custom'>('straight');

  // Straight track params
  const [length, setLength] = useState<string>('100');
  const [gauge, setGauge] = useState<string>('standard');

  // Arc track params
  const [radius, setRadius] = useState<string>('50');
  const [degrees, setDegrees] = useState<string>('90');
  const [direction, setDirection] = useState<'cw' | 'ccw'>('cw');

  // Custom SVG path
  const [svgPath, setSvgPath] = useState<string>('M 0 0 C 20 40, 40 40, 60 20 C 80 0, 100 0, 120 20 C 140 40, 160 40, 180 20 C 200 0, 220 -20, 240 -20 C 260 -20, 280 0, 300 20');

  const [trackName, setTrackName] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [creating, setCreating] = useState<boolean>(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [trackData, setTrackData] = useState<TrackResponse | null>(null);
  const [savedTracks, setSavedTracks] = useState<SavedTrack[]>([]);
  const [modalOpen, setModalOpen] = useState<boolean>(false);

  useEffect(() => {
    fetchSavedTracks();
  }, []);

  const fetchSavedTracks = async () => {
    try {
      const response = await fetch('https://react.brandonfremin.com/api/track');
      if (response.ok) {
        const tracks = await response.json();
        setSavedTracks(tracks.tracks);
      }
    } catch (error) {
      console.error('Failed to fetch saved tracks:', error);
    }
  };

  const handleDeleteTrack = async (trackId: string) => {
    try {
      const url = new URL('https://react.brandonfremin.com/api/track');
      url.searchParams.set('id', trackId);
      const response = await fetch(url.toString(), {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        setMessage({ type: 'success', text: 'Track deleted successfully!' });
        fetchSavedTracks();
      } else {
        setMessage({ type: 'error', text: 'Failed to delete track' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` });
    }
  };

  const handleTrackTypeChange = (_event: React.MouseEvent<HTMLElement>, newType: 'straight' | 'arc' | 'custom' | null) => {
    if (newType !== null) {
      setTrackType(newType);
      setTrackData(null);
      setMessage(null);
      setTrackName('');
    }
  };

  const generateSvgPath = (): string => {
    if (trackType === 'straight') {
      const len = parseFloat(length) || 100;
      return `M 0 0 L ${len} 0`;
    } else if (trackType === 'arc') {
      const r = parseFloat(radius) || 50;
      const deg = parseFloat(degrees) || 90;
      const rad = (deg * Math.PI) / 180;

      // Calculate end point - arc curves to the right
      const endX = r * Math.sin(rad);
      const endY = direction === 'cw'
        ? r * (1 - Math.cos(rad))
        : -r * (1 - Math.cos(rad));

      const largeArc = deg > 180 ? 1 : 0;
      const sweepFlag = direction === 'cw' ? 1 : 0;

      return `M 0 0 A ${r} ${r} 0 ${largeArc} ${sweepFlag} ${endX} ${endY}`;
    } else {
      return svgPath;
    }
  };

  const generateDefaultName = (): string => {
    if (trackType === 'straight') {
      return `Straight ${length}mm`;
    } else if (trackType === 'arc') {
      const dir = direction === 'cw' ? 'CW' : 'CCW';
      return `Arc R${radius} ${degrees}deg ${dir}`;
    } else {
      return 'Custom Track';
    }
  };

  const handlePreview = async () => {
    const pathToSubmit = generateSvgPath();

    if (!pathToSubmit.trim()) {
      setMessage({ type: 'error', text: 'Please enter valid track parameters' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const url = new URL('https://react.brandonfremin.com/api/preview');
      url.searchParams.set('path', pathToSubmit);
      url.searchParams.set('gauge', gauge);

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTrackData(data);
        setTrackName(generateDefaultName());
        setMessage({ type: 'success', text: 'Preview generated successfully!' });
      } else {
        setMessage({ type: 'error', text: `Failed to generate preview: ${response.statusText}` });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` });
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    const pathToSubmit = generateSvgPath();

    if (!pathToSubmit.trim()) {
      setMessage({ type: 'error', text: 'Please enter valid track parameters' });
      return;
    }

    if (!trackName.trim()) {
      setMessage({ type: 'error', text: 'Please preview the track first to generate a name' });
      return;
    }

    setCreating(true);
    setMessage(null);

    try {
      const response = await fetch('https://react.brandonfremin.com/api/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          trackName: trackName,
          trackData: trackData
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage({ type: 'success', text: `Track "${trackName}" created successfully!` });
        fetchSavedTracks();
        setTrackName('');
        setTrackData(null);
        setModalOpen(false);
      } else {
        setMessage({ type: 'error', text: `Failed to create track: ${response.statusText}` });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` });
    } finally {
      setCreating(false);
    }
  };

  return (
    <Box className="p-6 flex flex-col gap-3">
      <Box className="flex items-center justify-between">
        <Typography variant="h4" component="h1" className="font-bold">
          Track Editor
        </Typography>
        <Fab color="primary" size="small" onClick={() => setModalOpen(true)}>
          <AddIcon />
        </Fab>
      </Box>

      {/* Saved Tracks */}
      {savedTracks.length > 0 && (
        <Box className="mb-4">
          <Typography variant="h6" className="font-semibold mb-2">
            Saved Tracks
          </Typography>
          <Box className="flex gap-3 flex-wrap">
            {savedTracks.map((track) => (
              <Card key={track.id} className="relative" style={{ width: 150 }}>
                <CardContent className="p-2">
                  <Box className="flex items-center justify-between mb-1">
                    <Typography variant="caption" className="font-semibold truncate flex-1">
                      {track.name}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteTrack(track.id)}
                      sx={{ padding: '2px' }}
                      color="error"
                    >
                      <DeleteIcon sx={{ fontSize: 14 }} />
                    </IconButton>
                  </Box>
                  <TrackSvg data={track.data} size={120} />
                </CardContent>
              </Card>
            ))}
          </Box>
        </Box>
      )}

      {/* Create Track Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
      >
        <Box className="absolute top-1/2 left-1/2 bg-white p-6 rounded-lg shadow-xl flex flex-col gap-3" style={{ transform: 'translate(-50%, -50%)', width: '800px', height: '600px', overflow: 'auto' }}>
          <Typography variant="h5" component="h2" className="font-bold">
            Create New Track
          </Typography>
          
          {/* Track Name */}
          <TextField
            label="Track Name"
            value={trackName}
            onChange={(e) => setTrackName(e.target.value)}
            placeholder="Enter track name"
            variant="outlined"
            size="small"
            className="max-w-2xl"
          />

          {/* Track Type Selection */}
          <Box className="flex gap-4 items-center">
            <Typography variant="body1" className="font-semibold">Track Type:</Typography>
            <ToggleButtonGroup
              value={trackType}
              exclusive
              onChange={handleTrackTypeChange}
              size="small"
            >
              <ToggleButton value="straight">
                Straight
              </ToggleButton>
              <ToggleButton value="arc">
                Arc
              </ToggleButton>
              <ToggleButton value="custom">
                Custom SVG
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* Straight Track Inputs */}
          {trackType === 'straight' && (
            <Box className="flex gap-3 items-center max-w-2xl">
              <TextField
                label="Length"
                type="number"
                value={length}
                onChange={(e) => setLength(e.target.value)}
                variant="outlined"
                size="small"
                className="w-32"
              />
              <FormControl size="small" className="w-32">
                <InputLabel>Gauge</InputLabel>
                <Select
                  value={gauge}
                  onChange={(e) => setGauge(e.target.value)}
                  label="Gauge"
                >
                  <MenuItem value="standard">Standard</MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}

          {/* Arc Track Inputs */}
          {trackType === 'arc' && (
            <Box className="flex gap-3 items-center flex-wrap max-w-2xl">
              <TextField
                label="Radius"
                type="number"
                value={radius}
                onChange={(e) => setRadius(e.target.value)}
                variant="outlined"
                size="small"
                className="w-32"
              />
              <TextField
                label="Degrees"
                type="number"
                value={degrees}
                onChange={(e) => setDegrees(e.target.value)}
                variant="outlined"
                size="small"
                className="w-32"
              />
              <FormControl size="small" className="w-32">
                <InputLabel>Gauge</InputLabel>
                <Select
                  value={gauge}
                  onChange={(e) => setGauge(e.target.value)}
                  label="Gauge"
                >
                  <MenuItem value="standard">Standard</MenuItem>
                </Select>
              </FormControl>
              <ToggleButtonGroup
                value={direction}
                exclusive
                onChange={(_event, newDirection) => {
                  if (newDirection !== null) setDirection(newDirection);
                }}
                size="small"
              >
                <ToggleButton value="cw">
                  Clockwise
                </ToggleButton>
                <ToggleButton value="ccw">
                  Counter-CW
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          )}

          {/* Custom SVG Path Input */}
          {trackType === 'custom' && (
            <TextField
              label="SVG Path"
              multiline
              rows={2}
              value={svgPath}
              onChange={(e) => setSvgPath(e.target.value)}
              placeholder="Enter SVG path data (e.g., M 0 0 L 100 0)"
              variant="outlined"
              className="max-w-2xl"
            />
          )}

          {/* Action Buttons */}
          <Box className="flex gap-3">
            <Button
              variant="outlined"
              onClick={handlePreview}
              disabled={loading || creating}
              className="self-start"
            >
              {loading ? 'Generating Preview...' : 'Preview'}
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleCreate}
              disabled={loading || creating}
              className="self-start"
            >
              {creating ? 'Creating...' : 'Create Track'}
            </Button>
          </Box>

          {message && (
            <Alert severity={message.type} className="max-w-2xl">
              {message.text}
            </Alert>
          )}

          {trackData && (
            <>
              <Typography variant="h5" className="font-bold mt-4">
                SVG Preview
              </Typography>
              <Box className="border border-gray-300 bg-white p-4 inline-block w-fit">
                <TrackSvg data={trackData} size={400} />
              </Box>
            </>
          )}
        </Box>
      </Modal>
    </Box>
  );
}