import { useState, useEffect, useRef } from 'react';
import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Button, TextField, Fab, IconButton, Dialog, DialogTitle, DialogContent, DialogActions, ToggleButtonGroup, ToggleButton, Snackbar, Alert } from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import LockIcon from '@mui/icons-material/Lock';
import LinkIcon from '@mui/icons-material/Link';

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
    position: {
      x: number;
      y: number;
    };
    direction: {
      x: number;
      y: number;
    };
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

interface PlacedTrack {
  instanceId?: string;
  trackId: string;
  position: { x: number; y: number };
  rotation: number;
  fixed?: boolean;
}

interface LayoutData {
  counter: number;
  tracks: Array<{
    instanceId: string;
    trackId: string;
    x: number;
    y: number;
    rotation: number;
    fixed?: boolean;
    links?: Array<{
      anchorId: string;
      targetInstanceId: string;
      targetAnchorId: string;
    }>;
  }>;
}

interface Layout {
  id: string;
  name: string;
  data: LayoutData;
  metadata?: any;
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
  const [placedTracks, setPlacedTracks] = useState<PlacedTrack[]>([]);
  const [selectedTrackIndex, setSelectedTrackIndex] = useState<number | null>(null);
  const [isDraggingPlaced, setIsDraggingPlaced] = useState<boolean>(false);
  const [isUnlinkDragging, setIsUnlinkDragging] = useState<boolean>(false);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [dragStartPositions, setDragStartPositions] = useState<Map<number, { x: number; y: number }>>(new Map());
  const [hoveredTrackIndex, setHoveredTrackIndex] = useState<number | null>(null);
  const [mousePosition, setMousePosition] = useState<{ x: number; y: number } | null>(null);
  const rotationTimerRef = useRef<number | null>(null);
  const [isEditingTrack, setIsEditingTrack] = useState<boolean>(false);
  const [editingTrackIndex, setEditingTrackIndex] = useState<number | null>(null);
  const [editX, setEditX] = useState<string>('');
  const [editY, setEditY] = useState<string>('');
  const [editRotation, setEditRotation] = useState<string>('');
  const [firstAnchor, setFirstAnchor] = useState<{
    trackIndex: number;
    anchorId: string;
    worldPos: { x: number; y: number };
    angle: number;
  } | null>(null);
  const [toastOpen, setToastOpen] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string>('');
  const [toastSeverity, setToastSeverity] = useState<'error' | 'warning' | 'info' | 'success'>('error');
  const [viewBox, setViewBox] = useState<{ x: number; y: number; width: number; height: number }>({ x: -300, y: -200, width: 600, height: 400 });
  const [viewPadding, setViewPadding] = useState<number>(50);
  const [isEditingPadding, setIsEditingPadding] = useState<boolean>(false);
  const [tempPadding, setTempPadding] = useState<string>('50');
  const [snapRadius, setSnapRadius] = useState<number>(30);
  const [isEditingSnapRadius, setIsEditingSnapRadius] = useState<boolean>(false);
  const [tempSnapRadius, setTempSnapRadius] = useState<string>('30');

  const showToast = (message: string, severity: 'error' | 'warning' | 'info' | 'success' = 'error') => {
    setToastMessage(message);
    setToastSeverity(severity);
    setToastOpen(true);
  };

  useEffect(() => {
    fetchTracks();
    fetchLayouts();
  }, []);

  useEffect(() => {
    if (selectedLayout) {
      // Convert database format to PlacedTrack format
      const loadedTracks = selectedLayout.data?.tracks?.map(track => ({
        instanceId: track.instanceId,
        trackId: track.trackId,
        position: { x: track.x, y: track.y },
        rotation: track.rotation,
        fixed: track.fixed || false,
        links: track.links || []
      })) || [];
      setPlacedTracks(loadedTracks);
      
      // Update canvas size only when layout is initially loaded
      // Use a small timeout to ensure tracks data is available
      if (loadedTracks.length > 0 && tracks.length > 0) {
        setTimeout(() => updateCanvasSize(loadedTracks), 100);
      }
    } else {
      setPlacedTracks([]);
    }
  }, [selectedLayout]);

  const updateCanvasSize = (placedTracksToMeasure: PlacedTrack[]) => {
    // Calculate bounds of all tracks and fit viewBox to show them with padding
    if (placedTracksToMeasure.length === 0) {
      setViewBox({ x: -300, y: -200, width: 600, height: 400 });
      return;
    }

    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;

    // Find bounds using actual bounding boxes from track data
    placedTracksToMeasure.forEach((placedTrack) => {
      const track = tracks.find(t => t.id === placedTrack.trackId);
      if (!track || !track.data.boundingBox) return;

      const bbox = track.data.boundingBox;
      
      // Transform bounding box corners by rotation and translation
      const radians = (placedTrack.rotation * Math.PI) / 180;
      const cos = Math.cos(radians);
      const sin = Math.sin(radians);
      
      // Check all 4 corners of the bounding box
      const corners = [
        { x: bbox.xmin, y: bbox.ymin },
        { x: bbox.xmax, y: bbox.ymin },
        { x: bbox.xmin, y: bbox.ymax },
        { x: bbox.xmax, y: bbox.ymax }
      ];
      
      corners.forEach(corner => {
        const rotatedX = corner.x * cos - corner.y * sin;
        const rotatedY = corner.x * sin + corner.y * cos;
        const worldX = rotatedX + placedTrack.position.x;
        const worldY = rotatedY + placedTrack.position.y;
        
        minX = Math.min(minX, worldX);
        maxX = Math.max(maxX, worldX);
        minY = Math.min(minY, worldY);
        maxY = Math.max(maxY, worldY);
      });
    });

    // If no valid bounds found, use default
    if (!isFinite(minX) || !isFinite(maxX) || !isFinite(minY) || !isFinite(maxY)) {
      setViewBox({ x: -300, y: -200, width: 600, height: 400 });
      return;
    }

    // Add padding around the content
    minX -= viewPadding;
    maxX += viewPadding;
    minY -= viewPadding;
    maxY += viewPadding;

    const contentWidth = maxX - minX;
    const contentHeight = maxY - minY;

    // Maintain aspect ratio (3:2 like 600:400)
    const targetAspect = 600 / 400;
    const contentAspect = contentWidth / contentHeight;

    let finalWidth = contentWidth;
    let finalHeight = contentHeight;

    if (contentAspect > targetAspect) {
      // Content is wider - fit width and expand height
      finalHeight = finalWidth / targetAspect;
    } else {
      // Content is taller - fit height and expand width
      finalWidth = finalHeight * targetAspect;
    }

    // Center the viewBox on the center of the content bounds
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    setViewBox({ 
      x: centerX - finalWidth / 2, 
      y: centerY - finalHeight / 2, 
      width: finalWidth, 
      height: finalHeight 
    });
  };

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
        } else {
          // Clear selection when no layouts exist
          setSelectedLayoutId('');
          setSelectedLayout(null);
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
        // Clear selection if we're deleting the currently selected layout
        if (layoutId === selectedLayoutId) {
          setSelectedLayoutId('');
          setSelectedLayout(null);
        }
        await fetchLayouts();
      }
    } catch (error) {
      console.error('Failed to delete layout:', error);
    }
  };

  const handleDragStart = (e: React.DragEvent, trackId: string) => {
    e.dataTransfer.setData('trackId', trackId);
    e.dataTransfer.effectAllowed = 'copy';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const trackId = e.dataTransfer.getData('trackId');
    if (!trackId) return;

    // Get drop position in SVG coordinates
    const svg = (e.currentTarget as HTMLElement).querySelector('svg');
    if (!svg) {
      // Fallback if no SVG found yet (empty canvas)
      const canvasRect = (e.currentTarget as HTMLElement).getBoundingClientRect();
      const clientX = e.clientX - canvasRect.left;
      const clientY = e.clientY - canvasRect.top;
      const x = viewBox.x + (clientX / canvasRect.width) * viewBox.width;
      const y = viewBox.y + (clientY / canvasRect.height) * viewBox.height;
      
      // Use fallback coordinates
      handleDropWithCoords(trackId, x, y);
      return;
    }
    
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgPt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
    const x = svgPt.x;
    const y = svgPt.y;
    
    handleDropWithCoords(trackId, x, y);
  };

  const handleDropWithCoords = (trackId: string, x: number, y: number) => {

    // Check if we're in snap mode (firstAnchor is selected)
    if (firstAnchor) {
      // Find the track data to get anchor information
      const newTrackData = tracks.find(t => t.id === trackId);
      if (!newTrackData) return;

      // Get any available anchor (preferably the first one)
      const availableAnchor = newTrackData.data.anchors[0];

      if (!availableAnchor) {
        showToast('No anchor found on this track', 'warning');
        return;
      }

      // Check if firstAnchor already has 2 connections
      const anchorOccupancy = countAnchorConnections(firstAnchor.worldPos);
      if (anchorOccupancy >= 2) {
        showToast('Cannot snap: anchor already has 2 rails connected', 'warning');
        setFirstAnchor(null);
        return;
      }

      // Get the stationary track's instanceId
      const stationaryTrack = placedTracks[firstAnchor.trackIndex];
      if (!stationaryTrack.instanceId) {
        showToast('Cannot snap: stationary track not yet saved', 'warning');
        return;
      }

      // Send to server to add track and link it
      if (selectedLayout) {
        fetch('https://react.brandonfremin.com/api/layout', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            layoutId: selectedLayout.id,
            addTrack: {
              trackId,
              x: 0, // Server will calculate position
              y: 0,
              rotation: 0
            }
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.instanceId) {
            // Now send linkTrack request
            return fetch('https://react.brandonfremin.com/api/layout', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                layoutId: selectedLayout.id,
                linkTrack: {
                  stationaryInstanceId: stationaryTrack.instanceId,
                  stationaryAnchorId: firstAnchor.anchorId,
                  movedInstanceId: data.instanceId,
                  movedAnchorId: availableAnchor.id
                }
              })
            }).then(() => {
              // Reload layout to get updated positions
              return fetch(`https://react.brandonfremin.com/api/layout?layoutId=${selectedLayout.id}`);
            });
          }
        })
        .then(response => response?.json())
        .then(data => {
          if (data?.layouts) {
            // Find the current layout from the response
            const updatedLayout = data.layouts.find((l: any) => l.id === selectedLayout.id);
            if (updatedLayout?.data?.tracks) {
              // Update placed tracks from server
              const serverTracks = updatedLayout.data.tracks.map((t: any) => ({
                instanceId: t.instanceId,
                trackId: t.trackId,
                position: { x: t.x, y: t.y },
                rotation: t.rotation,
                fixed: t.fixed || false,
                links: t.links || []
              }));
              setPlacedTracks(serverTracks);
              updateCanvasSize(serverTracks);

              // Find the newly added track and set its remaining anchor as firstAnchor
              const newTrack = serverTracks[serverTracks.length - 1];
              const remainingAnchor = newTrackData.data.anchors.find(
                anchor => anchor.id !== availableAnchor.id
              );
              
              if (remainingAnchor && newTrack) {
                const newTrackIndex = serverTracks.length - 1;
                const anchorPos = getAnchorWorldPosition(newTrackIndex, remainingAnchor.id);
                if (anchorPos) {
                  setFirstAnchor({
                    trackIndex: newTrackIndex,
                    anchorId: remainingAnchor.id,
                    worldPos: { x: anchorPos.x, y: anchorPos.y },
                    angle: anchorPos.angle
                  });
                } else {
                  setFirstAnchor(null);
                }
              } else {
                setFirstAnchor(null);
              }
            }
          }
        })
        .catch(error => {
          console.error('Failed to link track:', error);
          showToast('Failed to link track', 'error');
        });
      }

      return;
    }

    // Normal drop behavior (no snap mode)
    const newTrack: PlacedTrack = {
      trackId,
      position: { x, y },
      rotation: 0
    };

    const updatedTracks = [...placedTracks, newTrack];
    setPlacedTracks(updatedTracks);

    // Send to server to update layout
    if (selectedLayout) {
      fetch('https://react.brandonfremin.com/api/layout', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          layoutId: selectedLayout.id,
          addTrack: {
            trackId,
            x,
            y,
            rotation: 0
          }
        })
      })
      .then(response => response.json())
      .then(data => {
        // Update the track with the instanceId returned from server
        if (data.instanceId) {
          setPlacedTracks(currentTracks => {
            const updated = [...currentTracks];
            const trackIndex = updated.findIndex(t => 
              t.trackId === trackId && 
              t.position.x === x && 
              t.position.y === y && 
              !t.instanceId
            );
            if (trackIndex !== -1) {
              updated[trackIndex] = {
                ...updated[trackIndex],
                instanceId: data.instanceId
              };
            }
            return updated;
          });
        }
      })
      .catch(error => console.error('Failed to update layout:', error));
    }
  };

  const handleTrackMouseDown = (e: React.MouseEvent, index: number) => {
    e.stopPropagation();
    
    // Ctrl+click to delete track
    if (e.ctrlKey) {
      handleDeleteTrack(index);
      return;
    }
    
    const placedTrack = placedTracks[index];

    // Don't allow dragging fixed tracks
    if (placedTrack.fixed) {
      return;
    }

    const track = tracks.find(t => t.id === placedTrack.trackId);
    if (!track) return;

    setSelectedTrackIndex(index);
    setIsDraggingPlaced(true);
    
    // Shift+click to unlink track and drag independently
    if (e.shiftKey) {
      setIsUnlinkDragging(true);
    }

    // Calculate offset from track position to mouse position
    const svg = (e.currentTarget.closest('svg') as SVGSVGElement);
    if (!svg) return;
    
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgPt = pt.matrixTransform(svg.getScreenCTM()?.inverse());

    setDragOffset({
      x: svgPt.x - placedTracks[index].position.x,
      y: svgPt.y - placedTracks[index].position.y
    });

    // Capture initial positions of tracks that will move
    // For unlink drag, only move the single track
    // For normal drag, move all connected tracks
    const initialPositions = new Map<number, { x: number; y: number }>();
    
    if (e.shiftKey) {
      // Only track the single piece being unlinked
      initialPositions.set(index, {
        x: placedTracks[index].position.x,
        y: placedTracks[index].position.y
      });
    } else {
      // Track all connected tracks
      const connectedTracks = getConnectedTracksStatic(index, placedTracks);
      connectedTracks.forEach((depth, trackIndex) => {
        initialPositions.set(trackIndex, {
          x: placedTracks[trackIndex].position.x,
          y: placedTracks[trackIndex].position.y
        });
      });
    }
    
    setDragStartPositions(initialPositions);
  };

  // Static helper function to get all connected tracks (doesn't depend on state)
  const getConnectedTracksStatic = (startIndex: number, tracksArray: PlacedTrack[]): Map<number, number> => {
    const connections = new Map<number, number>();
    const queue: Array<{index: number, depth: number}> = [{index: startIndex, depth: 0}];
    const visited = new Set<number>();
    visited.add(startIndex);

    while (queue.length > 0) {
      const {index, depth: currentDepth} = queue.shift()!;
      connections.set(index, currentDepth);

      const track = tracksArray[index];
      const links = track.links || [];

      for (const link of links) {
        const targetIndex = tracksArray.findIndex(t => t.instanceId === link.targetInstanceId);
        if (targetIndex !== -1 && !visited.has(targetIndex) && !tracksArray[targetIndex].fixed) {
          visited.add(targetIndex);
          queue.push({index: targetIndex, depth: currentDepth + 1});
        }
      }
    }

    return connections;
  };

  // Helper function to get all connected tracks recursively
  const getConnectedTracks = (startIndex: number, depth: number = 0, visited: Set<number> = new Set()): Map<number, number> => {
    const connections = new Map<number, number>(); // trackIndex -> depth
    const queue: Array<{index: number, depth: number}> = [{index: startIndex, depth: 0}];
    visited.add(startIndex);

    while (queue.length > 0) {
      const {index, depth: currentDepth} = queue.shift()!;
      connections.set(index, currentDepth);

      const track = placedTracks[index];
      const links = track.links || [];

      for (const link of links) {
        const targetIndex = placedTracks.findIndex(t => t.instanceId === link.targetInstanceId);
        if (targetIndex !== -1 && !visited.has(targetIndex) && !placedTracks[targetIndex].fixed) {
          visited.add(targetIndex);
          queue.push({index: targetIndex, depth: currentDepth + 1});
        }
      }
    }

    return connections;
  };

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    const svg = e.currentTarget as unknown as SVGSVGElement;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgPt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
    const mouseX = svgPt.x;
    const mouseY = svgPt.y;
    
    // Update mouse position for closest track calculation
    setMousePosition({ x: mouseX, y: mouseY });

    if (!isDraggingPlaced || selectedTrackIndex === null) return;

    const newX = mouseX - dragOffset.x;
    const newY = mouseY - dragOffset.y;

    // Calculate delta from initial position
    const initialPos = dragStartPositions.get(selectedTrackIndex);
    if (!initialPos) return;

    const deltaX = newX - initialPos.x;
    const deltaY = newY - initialPos.y;

    const updatedTracks = [...placedTracks];
    
    // Move all connected tracks by the same delta from their initial positions
    dragStartPositions.forEach((startPos, trackIndex) => {
      updatedTracks[trackIndex] = {
        ...updatedTracks[trackIndex],
        position: {
          x: startPos.x + deltaX,
          y: startPos.y + deltaY
        }
      };
    });
    
    setPlacedTracks(updatedTracks);
  };

  const handleDeleteTrack = (index: number) => {
    const trackToDelete = placedTracks[index];
    if (!trackToDelete.instanceId || !selectedLayout) return;

    // Remove from local state immediately
    const updatedTracks = placedTracks.filter((_, i) => i !== index);
    setPlacedTracks(updatedTracks);

    // Send delete request to server
    fetch('https://react.brandonfremin.com/api/layout', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        layoutId: selectedLayout.id,
        removeTrack: {
          instanceId: trackToDelete.instanceId
        }
      })
    }).catch(error => {
      console.error('Failed to delete track:', error);
      // Restore track on error
      setPlacedTracks(placedTracks);
    });
  };

  const handleToggleFixed = (e: React.MouseEvent, index: number) => {
    e.stopPropagation();
    
    const track = placedTracks[index];
    if (!track.instanceId || !selectedLayout) return;

    const newFixedState = !track.fixed;

    // Update local state optimistically
    setPlacedTracks(currentTracks => 
      currentTracks.map((t, i) => 
        i === index ? { ...t, fixed: newFixedState } : t
      )
    );

    // Send to server
    fetch('https://react.brandonfremin.com/api/layout', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        layoutId: selectedLayout.id,
        fixTrack: {
          instanceId: track.instanceId,
          fixed: newFixedState
        }
      })
    }).catch(error => {
      console.error('Failed to update track fixed state:', error);
      // Restore on error
      setPlacedTracks(currentTracks => 
        currentTracks.map((t, i) => 
          i === index ? { ...t, fixed: track.fixed } : t
        )
      );
    });
  };

  const findClosestTrack = (): number | null => {
    if (!mousePosition || placedTracks.length === 0) return null;

    let closestIndex = -1;
    let minDistance = Infinity;

    placedTracks.forEach((placedTrack, index) => {
      const dx = placedTrack.position.x - mousePosition.x;
      const dy = placedTrack.position.y - mousePosition.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < minDistance) {
        minDistance = distance;
        closestIndex = index;
      }
    });

    return closestIndex >= 0 ? closestIndex : null;
  };

  const getAnchorWorldPosition = (trackIndex: number, anchorId: string) => {
    const placedTrack = placedTracks[trackIndex];
    const track = tracks.find(t => t.id === placedTrack.trackId);
    if (!track) {
      console.log(`getAnchorWorldPosition: track not found for trackId ${placedTrack.trackId}`);
      return null;
    }

    const anchor = track.data.anchors.find(a => a.id === anchorId);
    if (!anchor) {
      console.log(`getAnchorWorldPosition: anchor ${anchorId} not found`);
      return null;
    }

    // Use the explicit position data from the anchor
    const localX = anchor.position.x;
    const localY = anchor.position.y;

    // Apply rotation
    const radians = (placedTrack.rotation * Math.PI) / 180;
    const cos = Math.cos(radians);
    const sin = Math.sin(radians);
    const rotatedX = localX * cos - localY * sin;
    const rotatedY = localX * sin + localY * cos;

    // Apply translation
    const worldX = rotatedX + placedTrack.position.x;
    const worldY = rotatedY + placedTrack.position.y;

    // Calculate anchor angle from direction vector
    const dirX = anchor.direction.x;
    const dirY = anchor.direction.y;
    const localAngle = Math.atan2(dirY, dirX) * 180 / Math.PI;
    const worldAngle = localAngle + placedTrack.rotation;

    return { x: worldX, y: worldY, angle: worldAngle };
  };

  const countAnchorConnections = (anchorWorldPos: { x: number; y: number }): number => {
    const tolerance = 5; // pixels
    let count = 0;
    
    placedTracks.forEach((placedTrack, trackIndex) => {
      const track = tracks.find(t => t.id === placedTrack.trackId);
      if (!track) return;
      
      track.data.anchors.forEach(anchor => {
        const pos = getAnchorWorldPosition(trackIndex, anchor.id);
        if (!pos) return;
        
        const distance = Math.sqrt(
          Math.pow(pos.x - anchorWorldPos.x, 2) + 
          Math.pow(pos.y - anchorWorldPos.y, 2)
        );
        
        if (distance < tolerance) {
          count++;
        }
      });
    });
    
    return count;
  };

  const findNearestAnchor = (clickX: number, clickY: number): { trackIndex: number; anchorId: string } | null => {
    let nearestAnchor: { trackIndex: number; anchorId: string } | null = null;
    let minDistance = Infinity;

    console.log('Finding nearest anchor to click:', clickX, clickY);
    console.log('Total placed tracks:', placedTracks.length);

    placedTracks.forEach((placedTrack, trackIndex) => {
      // Allow selecting anchors on fixed tracks (they can be first anchor)
      
      const track = tracks.find(t => t.id === placedTrack.trackId);
      if (!track) {
        console.log(`Track not found for trackIndex ${trackIndex}`);
        return;
      }

      console.log(`Track ${trackIndex} has ${track.data.anchors?.length || 0} anchors`);

      if (!track.data.anchors) {
        console.log(`No anchors array for track ${trackIndex}`);
        return;
      }

      track.data.anchors.forEach((anchor) => {
        console.log(`Processing anchor ${anchor.id}, tangent:`, anchor.tangent);
        const anchorPos = getAnchorWorldPosition(trackIndex, anchor.id);
        if (!anchorPos) {
          console.log(`getAnchorWorldPosition returned null for anchor ${anchor.id}`);
          return;
        }

        const dx = anchorPos.x - clickX;
        const dy = anchorPos.y - clickY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        console.log(`Anchor ${anchor.id} at (${anchorPos.x.toFixed(1)}, ${anchorPos.y.toFixed(1)}), distance: ${distance.toFixed(1)}`);

        if (distance < minDistance) {
          minDistance = distance;
          nearestAnchor = { trackIndex, anchorId: anchor.id };
        }
      });
    });

    console.log('Nearest anchor:', nearestAnchor, 'distance:', minDistance.toFixed(1));
    return nearestAnchor;
  };

  const handleAnchorClick = (e: React.MouseEvent, clickX?: number, clickY?: number) => {
    e.stopPropagation();

    console.log('handleAnchorClick called with:', clickX, clickY);

    // If no specific coordinates, find nearest anchor to click
    let trackIndex: number;
    let anchorId: string;

    if (clickX !== undefined && clickY !== undefined) {
      const nearest = findNearestAnchor(clickX, clickY);
      if (!nearest) {
        console.log('No nearest anchor found');
        return;
      }
      trackIndex = nearest.trackIndex;
      anchorId = nearest.anchorId;
      console.log('Selected anchor:', anchorId, 'on track', trackIndex);
    } else {
      // This shouldn't happen, but fallback
      console.log('No click coordinates provided');
      return;
    }

    const placedTrack = placedTracks[trackIndex];
    
    const anchorPos = getAnchorWorldPosition(trackIndex, anchorId);
    if (!anchorPos) return;
    
    // Get anchor types
    const track = tracks.find(t => t.id === placedTrack.trackId);
    if (!track) return;
    
    const anchor = track.data.anchors.find(a => a.id === anchorId);
    if (!anchor) return;

    if (!firstAnchor) {
      // First anchor selected - store info
      setFirstAnchor({
        trackIndex,
        anchorId,
        worldPos: anchorPos,
        angle: anchorPos.angle
      });
    } else {
      // Second anchor selected - perform snap
      
      // Rule 1: Can't move a locked track
      if (placedTrack.fixed) {
        console.log('Cannot snap: second track is locked');
        showToast('Cannot snap: target track is locked', 'warning');
        setFirstAnchor(null);
        return;
      }
      
      if (firstAnchor.trackIndex === trackIndex) {
        // Can't snap track to itself
        setFirstAnchor(null);
        return;
      }
      
      // Rule 2: Check if anchor already has 2 rails connected
      const anchorOccupancy = countAnchorConnections(firstAnchor.worldPos);
      if (anchorOccupancy >= 2) {
        console.log('Cannot snap: anchor already has 2 rails connected');
        showToast('Cannot snap: anchor already has 2 rails connected', 'warning');
        setFirstAnchor(null);
        return;
      }

      // Get instance IDs
      const firstTrack = placedTracks[firstAnchor.trackIndex];
      if (!firstTrack.instanceId || !placedTrack.instanceId) {
        showToast('Cannot snap: tracks not yet saved', 'warning');
        setFirstAnchor(null);
        return;
      }

      // Send linkTrack request to server
      if (selectedLayout) {
        fetch('https://react.brandonfremin.com/api/layout', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            layoutId: selectedLayout.id,
            linkTrack: {
              stationaryInstanceId: firstTrack.instanceId,
              stationaryAnchorId: firstAnchor.anchorId,
              movedInstanceId: placedTrack.instanceId,
              movedAnchorId: anchorId
            }
          })
        })
        .then(() => {
          // Reload layout to get updated positions
          return fetch(`https://react.brandonfremin.com/api/layout?layoutId=${selectedLayout.id}`);
        })
        .then(response => response.json())
        .then(data => {
          if (data?.layouts) {
            // Find the current layout from the response
            const updatedLayout = data.layouts.find((l: any) => l.id === selectedLayout.id);
            if (updatedLayout?.data?.tracks) {
              // Update placed tracks from server
              const serverTracks = updatedLayout.data.tracks.map((t: any) => ({
                instanceId: t.instanceId,
                trackId: t.trackId,
                position: { x: t.x, y: t.y },
                rotation: t.rotation,
                fixed: t.fixed || false,
                links: t.links || []
              }));
              setPlacedTracks(serverTracks);
              updateCanvasSize(serverTracks);
            }
          }
        })
        .catch(error => {
          console.error('Failed to link track:', error);
          showToast('Failed to link track', 'error');
        });
      }

      // Clear selection
      setFirstAnchor(null);
    }
  };

  const handleTrackDoubleClick = (e: React.MouseEvent, index: number) => {
    e.stopPropagation();
    
    const placedTrack = placedTracks[index];
    const track = tracks.find(t => t.id === placedTrack.trackId);
    if (!track) return;

    // Get click position in SVG coordinates
    const svg = (e.currentTarget.closest('svg') as SVGSVGElement);
    if (!svg) return;
    
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgPt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
    const clickX = svgPt.x;
    const clickY = svgPt.y;

    // Check if click is near any anchor (within 20 pixels)
    const anchorThreshold = 20;
    let nearestAnchor: { id: string; distance: number } | null = null;

    track.data.anchors.forEach((anchor) => {
      const anchorPos = getAnchorWorldPosition(index, anchor.id);
      if (!anchorPos) return;

      const dx = anchorPos.x - clickX;
      const dy = anchorPos.y - clickY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < anchorThreshold) {
        if (!nearestAnchor || distance < nearestAnchor.distance) {
          nearestAnchor = { id: anchor.id, distance };
        }
      }
    });

    // If near an anchor, check if it's already fully connected
    if (nearestAnchor) {
      const anchorPos = getAnchorWorldPosition(index, nearestAnchor.id);
      const anchor = track.data.anchors.find(a => a.id === nearestAnchor!.id);
      if (anchorPos && anchor) {
        // Check if anchor already has 2 connections
        const connections = countAnchorConnections(anchorPos);
        if (connections >= 2) {
          showToast('Anchor is already fully connected', 'info');
          return;
        }
        
        // Switch to snap mode and select the anchor
        setFirstAnchor({
          trackIndex: index,
          anchorId: nearestAnchor.id,
          worldPos: anchorPos,
          angle: anchorPos.angle
        });
      }
      return;
    }

    // Otherwise, open edit modal with current values
    setEditingTrackIndex(index);
    setEditX(placedTrack.position.x.toFixed(2));
    setEditY(placedTrack.position.y.toFixed(2));
    setEditRotation(placedTrack.rotation.toString());
    setIsEditingTrack(true);
  };

  const handleSaveTrackEdit = () => {
    if (editingTrackIndex === null || !selectedLayout) return;

    const placedTrack = placedTracks[editingTrackIndex];
    
    // Don't allow editing locked tracks
    if (placedTrack.fixed) {
      return;
    }
    
    const newX = parseFloat(editX);
    const newY = parseFloat(editY);
    const newRotation = parseFloat(editRotation);

    // Validate inputs
    if (isNaN(newX) || isNaN(newY) || isNaN(newRotation)) {
      return;
    }

    // Calculate deltas
    const deltaX = newX - placedTrack.position.x;
    const deltaY = newY - placedTrack.position.y;
    const rotationDelta = newRotation - placedTrack.rotation;

    // Find all connected tracks
    const connectedTracks = getConnectedTracksStatic(editingTrackIndex, placedTracks);
    
    // Calculate rotation transformation
    const rotationDeltaRad = (rotationDelta * Math.PI) / 180;
    const cosDelta = Math.cos(rotationDeltaRad);
    const sinDelta = Math.sin(rotationDeltaRad);
    const pivotX = placedTrack.position.x;
    const pivotY = placedTrack.position.y;

    // Update local state for all connected tracks
    setPlacedTracks(currentTracks => 
      currentTracks.map((t, i) => {
        if (i === editingTrackIndex) {
          // Main track: apply new position and rotation
          return { 
            ...t, 
            position: { x: newX, y: newY },
            rotation: newRotation % 360
          };
        } else if (connectedTracks.has(i)) {
          // Connected track: rotate around pivot, then translate
          const relX = t.position.x - pivotX;
          const relY = t.position.y - pivotY;
          const rotatedRelX = relX * cosDelta - relY * sinDelta;
          const rotatedRelY = relX * sinDelta + relY * cosDelta;
          
          return {
            ...t,
            position: {
              x: newX + rotatedRelX,
              y: newY + rotatedRelY
            },
            rotation: (t.rotation + rotationDelta) % 360
          };
        }
        return t;
      })
    );

    // Send to server if track has instanceId
    // The backend will handle moving all connected tracks
    if (placedTrack.instanceId) {
      fetch('https://react.brandonfremin.com/api/layout', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          layoutId: selectedLayout.id,
          addTrack: {
            instanceId: placedTrack.instanceId,
            trackId: placedTrack.trackId,
            x: newX,
            y: newY,
            rotation: newRotation % 360
          }
        })
      }).catch(error => console.error('Failed to update track:', error));
    }

    // Close modal
    setIsEditingTrack(false);
    setEditingTrackIndex(null);
  };

  const handleDeleteTrackFromModal = () => {
    if (editingTrackIndex === null) return;
    
    const placedTrack = placedTracks[editingTrackIndex];
    
    // Don't allow deleting locked tracks
    if (placedTrack.fixed) {
      showToast('Cannot delete: track is locked', 'warning');
      return;
    }
    
    handleDeleteTrack(editingTrackIndex);
    setIsEditingTrack(false);
    setEditingTrackIndex(null);
  };

  const handleTrackKeyDown = (e: React.KeyboardEvent, index: number) => {
    const placedTrack = placedTracks[index];
    
    // Don't allow rotating fixed tracks
    if (placedTrack.fixed) {
      return;
    }

    // Check for rotation keys: 'A' rotates left, 'D' rotates right
    let rotationDelta = 0;
    if (e.key === 'a' || e.key === 'A') {
      rotationDelta = -15;
    } else if (e.key === 'd' || e.key === 'D') {
      rotationDelta = 15;
    } else {
      return; // Not a rotation key
    }

    e.preventDefault();
    e.stopPropagation();

    const newRotation = (placedTrack.rotation + rotationDelta) % 360;

    // Find all connected tracks
    const connectedTracks = getConnectedTracksStatic(index, placedTracks);
    
    // Calculate rotation transformation
    const rotationDeltaRad = (rotationDelta * Math.PI) / 180;
    const cosDelta = Math.cos(rotationDeltaRad);
    const sinDelta = Math.sin(rotationDeltaRad);
    const pivotX = placedTrack.position.x;
    const pivotY = placedTrack.position.y;

    // Update local state immediately for all connected tracks
    setPlacedTracks(currentTracks => 
      currentTracks.map((t, i) => {
        if (i === index) {
          // Main track: just update rotation
          return { ...t, rotation: newRotation };
        } else if (connectedTracks.has(i)) {
          // Connected track: rotate around pivot
          const relX = t.position.x - pivotX;
          const relY = t.position.y - pivotY;
          const rotatedRelX = relX * cosDelta - relY * sinDelta;
          const rotatedRelY = relX * sinDelta + relY * cosDelta;
          
          return {
            ...t,
            position: {
              x: pivotX + rotatedRelX,
              y: pivotY + rotatedRelY
            },
            rotation: (t.rotation + rotationDelta) % 360
          };
        }
        return t;
      })
    );

    // Clear existing timer
    if (rotationTimerRef.current) {
      clearTimeout(rotationTimerRef.current);
    }

    // Set up debounced server update
    rotationTimerRef.current = setTimeout(() => {
      // Send to server if track has instanceId
      if (placedTrack.instanceId && selectedLayout) {
        fetch('https://react.brandonfremin.com/api/layout', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            layoutId: selectedLayout.id,
            addTrack: {
              instanceId: placedTrack.instanceId,
              trackId: placedTrack.trackId,
              x: placedTrack.position.x,
              y: placedTrack.position.y,
              rotation: newRotation
            }
          })
        }).catch(error => console.error('Failed to update track rotation:', error));
      }
    }, 500); // Wait 500ms after last rotation before sending to server
  };

  const handleCanvasMouseUp = () => {
    if (isDraggingPlaced && selectedTrackIndex !== null) {
      // Check for nearby anchors to auto-link
      const draggedTrack = placedTracks[selectedTrackIndex];
      const draggedTrackData = tracks.find(t => t.id === draggedTrack.trackId);
      
      console.log('Mouse up - checking for snap. Dragged track:', draggedTrack);
      console.log('Snap radius:', snapRadius);
      
      if (draggedTrackData && !draggedTrack.fixed) {
        const snapThreshold = snapRadius; // Distance threshold for auto-snap
        let bestSnap: {
          draggedAnchorId: string;
          targetTrackIndex: number;
          targetAnchorId: string;
          distance: number;
        } | null = null;

        // Check all anchors on the dragged track
        draggedTrackData.data.anchors.forEach(draggedAnchor => {
          const draggedAnchorPos = getAnchorWorldPosition(selectedTrackIndex, draggedAnchor.id);
          if (!draggedAnchorPos) return;

          // Check against all other tracks
          placedTracks.forEach((otherTrack, otherIndex) => {
            if (otherIndex === selectedTrackIndex) return;

            const otherTrackData = tracks.find(t => t.id === otherTrack.trackId);
            if (!otherTrackData) return;

            otherTrackData.data.anchors.forEach(otherAnchor => {
              const otherAnchorPos = getAnchorWorldPosition(otherIndex, otherAnchor.id);
              if (!otherAnchorPos) return;

              // Check if either anchor already has 2 connections
              const draggedConnections = countAnchorConnections(draggedAnchorPos);
              const otherConnections = countAnchorConnections(otherAnchorPos);
              if (draggedConnections >= 2 || otherConnections >= 2) return;

              // Calculate distance
              const dx = draggedAnchorPos.x - otherAnchorPos.x;
              const dy = draggedAnchorPos.y - otherAnchorPos.y;
              const distance = Math.sqrt(dx * dx + dy * dy);

              console.log(`Checking: ${draggedAnchor.id} to ${otherAnchor.id}, distance: ${distance.toFixed(1)}`);

              if (distance < snapThreshold && (!bestSnap || distance < bestSnap.distance)) {
                console.log('Found potential snap!');
                bestSnap = {
                  draggedAnchorId: draggedAnchor.id,
                  targetTrackIndex: otherIndex,
                  targetAnchorId: otherAnchor.id,
                  distance
                };
              }
            });
          });
        });

        // If we found a nearby anchor, snap to it
        if (bestSnap) {
          console.log('Snapping to:', bestSnap);
          const targetTrack = placedTracks[bestSnap.targetTrackIndex];

          if (draggedTrack.instanceId && targetTrack.instanceId && selectedLayout) {
            // Send linkTrack request to server
            fetch('https://react.brandonfremin.com/api/layout', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                layoutId: selectedLayout.id,
                linkTrack: {
                  stationaryInstanceId: targetTrack.instanceId,
                  stationaryAnchorId: bestSnap.targetAnchorId,
                  movedInstanceId: draggedTrack.instanceId,
                  movedAnchorId: bestSnap.draggedAnchorId
                }
              })
            })
            .then(() => {
              // Reload layout to get updated positions
              return fetch(`https://react.brandonfremin.com/api/layout?layoutId=${selectedLayout.id}`);
            })
            .then(response => response.json())
            .then(data => {
              if (data?.layouts) {
                // Find the current layout from the response
                const updatedLayout = data.layouts.find((l: any) => l.id === selectedLayout.id);
                if (updatedLayout?.data?.tracks) {
                  // Update placed tracks from server
                  const serverTracks = updatedLayout.data.tracks.map((t: any) => ({
                    instanceId: t.instanceId,
                    trackId: t.trackId,
                    position: { x: t.x, y: t.y },
                    rotation: t.rotation,
                    fixed: t.fixed || false,
                    links: t.links || []
                  }));
                  setPlacedTracks(serverTracks);
                  updateCanvasSize(serverTracks);
                }
              }
              // Clean up drag state after successful link
              setIsDraggingPlaced(false);
              setSelectedTrackIndex(null);
            })
            .catch(error => {
              console.error('Failed to link track:', error);
              showToast('Failed to link track', 'error');
              // Clean up drag state even on error
              setIsDraggingPlaced(false);
              setSelectedTrackIndex(null);
            });
            return;
          }
        }
      }

      // No snap found, just save the current position
      const placedTrack = placedTracks[selectedTrackIndex];

      // Send to server to update layout
      if (selectedLayout) {
        // If we're in unlink-drag mode, send unlinkTrack with new position
        if (isUnlinkDragging) {
          fetch('https://react.brandonfremin.com/api/layout', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              layoutId: selectedLayout.id,
              unlinkTrack: {
                instanceId: placedTrack.instanceId,
                x: placedTrack.position.x,
                y: placedTrack.position.y
              }
            })
          })
          .then(() => {
            // Reload layout to get updated links
            return fetch(`https://react.brandonfremin.com/api/layout?layoutId=${selectedLayout.id}`);
          })
          .then(response => response.json())
          .then(data => {
            if (data?.layouts) {
              const updatedLayout = data.layouts.find((l: any) => l.id === selectedLayout.id);
              if (updatedLayout?.data?.tracks) {
                const serverTracks = updatedLayout.data.tracks.map((t: any) => ({
                  instanceId: t.instanceId,
                  trackId: t.trackId,
                  position: { x: t.x, y: t.y },
                  rotation: t.rotation,
                  fixed: t.fixed || false,
                  links: t.links || []
                }));
                setPlacedTracks(serverTracks);
                updateCanvasSize(serverTracks);
              }
            }
          })
          .catch(error => console.error('Failed to unlink track:', error));
        } else {
          // Normal drag - use addTrack to move connected pieces
          fetch('https://react.brandonfremin.com/api/layout', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              layoutId: selectedLayout.id,
              addTrack: {
                instanceId: placedTrack.instanceId,
                trackId: placedTrack.trackId,
                x: placedTrack.position.x,
                y: placedTrack.position.y,
                rotation: placedTrack.rotation
              }
            })
          }).catch(error => console.error('Failed to update layout:', error));
        }
      }
    }

    setIsDraggingPlaced(false);
    setSelectedTrackIndex(null);
    setIsUnlinkDragging(false);
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
      <Dialog open={isCreatingLayout} onClose={() => setIsCreatingLayout(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Layout</DialogTitle>
        <DialogContent>
          <TextField
            label="Layout Name"
            value={newLayoutName}
            onChange={(e) => setNewLayoutName(e.target.value)}
            fullWidth
            autoFocus
            margin="dense"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCreatingLayout(false)}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleCreateLayout}>
            Create
          </Button>
        </DialogActions>
      </Dialog>

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
            <Box className="ml-auto flex items-center gap-2">
              <Typography variant="caption" color="text.secondary">
                ViewBox: ({viewBox.x.toFixed(0)}, {viewBox.y.toFixed(0)}) {viewBox.width.toFixed(0)}×{viewBox.height.toFixed(0)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                | Padding:
              </Typography>
              {isEditingPadding ? (
                <input
                  type="number"
                  value={tempPadding}
                  onChange={(e) => setTempPadding(e.target.value)}
                  onBlur={() => {
                    const val = parseInt(tempPadding);
                    if (!isNaN(val) && val >= 0) {
                      setViewPadding(val);
                    } else {
                      setTempPadding(viewPadding.toString());
                    }
                    setIsEditingPadding(false);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      const val = parseInt(tempPadding);
                      if (!isNaN(val) && val >= 0) {
                        setViewPadding(val);
                      } else {
                        setTempPadding(viewPadding.toString());
                      }
                      setIsEditingPadding(false);
                    }
                  }}
                  autoFocus
                  style={{ width: '60px', fontSize: '12px', padding: '2px 4px' }}
                />
              ) : (
                <Typography
                  variant="caption"
                  color="primary"
                  onClick={() => {
                    setTempPadding(viewPadding.toString());
                    setIsEditingPadding(true);
                  }}
                  style={{ cursor: 'pointer', textDecoration: 'underline' }}
                >
                  {viewPadding}px
                </Typography>
              )}
              <Typography variant="caption" color="text.secondary">
                | Snap:
              </Typography>
              {isEditingSnapRadius ? (
                <input
                  type="number"
                  value={tempSnapRadius}
                  onChange={(e) => setTempSnapRadius(e.target.value)}
                  onBlur={() => {
                    const val = parseInt(tempSnapRadius);
                    if (!isNaN(val) && val >= 0) {
                      setSnapRadius(val);
                    } else {
                      setTempSnapRadius(snapRadius.toString());
                    }
                    setIsEditingSnapRadius(false);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      const val = parseInt(tempSnapRadius);
                      if (!isNaN(val) && val >= 0) {
                        setSnapRadius(val);
                      } else {
                        setTempSnapRadius(snapRadius.toString());
                      }
                      setIsEditingSnapRadius(false);
                    }
                  }}
                  autoFocus
                  style={{ width: '60px', fontSize: '12px', padding: '2px 4px' }}
                />
              ) : (
                <Typography
                  variant="caption"
                  color="primary"
                  onClick={() => {
                    setTempSnapRadius(snapRadius.toString());
                    setIsEditingSnapRadius(true);
                  }}
                  style={{ cursor: 'pointer', textDecoration: 'underline' }}
                  title="Auto-snap radius when dragging tracks"
                >
                  {snapRadius}px
                </Typography>
              )}
              <IconButton
                size="small"
                onClick={() => updateCanvasSize(placedTracks)}
                title="Recenter and resize view to fit all tracks"
              >
                <span style={{ fontSize: '16px' }}>🎯</span>
              </IconButton>
            </Box>
          </Box>
          <Box 
            className="border border-gray-300 bg-gray-50 p-4 relative" 
            style={{ minHeight: '600px' }}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            {placedTracks.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                Drag and drop tracks here
              </Typography>
            ) : (
              <svg 
                width="100%" 
                height="600" 
                viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`}
                preserveAspectRatio="xMidYMid meet"
                style={{ position: 'absolute', top: 0, left: 0, cursor: isDraggingPlaced ? 'grabbing' : firstAnchor ? 'crosshair' : 'default' }}
                onMouseMove={handleCanvasMouseMove}
                onMouseUp={handleCanvasMouseUp}
                onMouseLeave={handleCanvasMouseUp}
                tabIndex={0}
                onKeyDown={(e) => {
                  const closestIndex = findClosestTrack();
                  if (closestIndex !== null) {
                    handleTrackKeyDown(e, closestIndex);
                  }
                }}
                onClick={(e) => {
                  if (firstAnchor) {
                    const svg = e.currentTarget as SVGSVGElement;
                    const pt = svg.createSVGPoint();
                    pt.x = e.clientX;
                    pt.y = e.clientY;
                    const svgPt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
                    handleAnchorClick(e, svgPt.x, svgPt.y);
                  }
                }}
              >
                {placedTracks.map((placedTrack, index) => {
                  const track = tracks.find(t => t.id === placedTrack.trackId);
                  if (!track) return null;
                  
                  const isSelected = selectedTrackIndex === index;
                  
                  return (
                    <g 
                      key={index}
                      transform={`translate(${placedTrack.position.x}, ${placedTrack.position.y}) rotate(${placedTrack.rotation})`}
                    >
                      {/* Invisible bounding box for easier selection */}
                      <rect
                        x={track.data.boundingBox.xmin}
                        y={track.data.boundingBox.ymin}
                        width={track.data.boundingBox.xmax - track.data.boundingBox.xmin}
                        height={track.data.boundingBox.ymax - track.data.boundingBox.ymin}
                        fill="transparent"
                        style={{ cursor: placedTrack.fixed ? 'not-allowed' : 'grab' }}
                        onMouseDown={(e) => handleTrackMouseDown(e, index)}
                        onDoubleClick={(e) => handleTrackDoubleClick(e, index)}
                        onMouseEnter={() => setHoveredTrackIndex(index)}
                        onMouseLeave={() => setHoveredTrackIndex(null)}
                        onContextMenu={(e) => {
                          e.preventDefault();
                          handleToggleFixed(e, index);
                        }}
                        pointerEvents={firstAnchor ? 'none' : 'auto'}
                      />

                      {/* Selection highlight - bounding box rectangle */}
                      {isSelected && (
                        <rect
                          x={track.data.boundingBox.xmin}
                          y={track.data.boundingBox.ymin}
                          width={track.data.boundingBox.xmax - track.data.boundingBox.xmin}
                          height={track.data.boundingBox.ymax - track.data.boundingBox.ymin}
                          fill="none"
                          stroke="#2196f3"
                          strokeWidth="2"
                          strokeDasharray="4"
                          pointerEvents="none"
                        />
                      )}

                      {/* Centerlines */}
                      {track.data.centerlines.map((centerline, i) => (
                        <path
                          key={`centerline-${i}`}
                          d={centerline.path}
                          stroke="blue"
                          strokeWidth="0.5"
                          fill="none"
                          opacity="0.5"
                          pointerEvents="none"
                        />
                      ))}

                      {/* Ties */}
                      {track.data.ties.map((tie, i) => (
                        <path
                          key={`tie-${i}`}
                          d={tie.path}
                          fill="brown"
                          stroke="none"
                          pointerEvents="none"
                        />
                      ))}

                      {/* Rails */}
                      {track.data.rails.map((rail, i) => (
                        <polygon
                          key={`rail-${i}`}
                          points={rail.path}
                          fill="#404040"
                          stroke="#202020"
                          strokeWidth="0.2"
                          pointerEvents="none"
                        />
                      ))}

                      {/* Lock indicator for fixed tracks */}
                      {placedTrack.fixed && (
                        <g transform={`translate(${track.data.boundingBox.xmin + 5}, ${track.data.boundingBox.ymin + 5})`}>
                          <circle cx="10" cy="10" r="10" fill="white" opacity="0.9" pointerEvents="none" />
                          <foreignObject x="2" y="2" width="16" height="16" pointerEvents="none">
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                              <LockIcon sx={{ fontSize: 16, color: '#f44336' }} />
                            </div>
                          </foreignObject>
                        </g>
                      )}
                    </g>
                  );
                })}

                {/* Render anchors in two passes: non-dragged tracks first, then dragged track on top */}
                {placedTracks.map((placedTrack, index) => {
                  // Skip dragged track in first pass
                  if (isDraggingPlaced && selectedTrackIndex === index) return null;

                  const track = tracks.find(t => t.id === placedTrack.trackId);
                  if (!track) return null;

                  return (
                    <g
                      key={`anchors-${index}`}
                      transform={`translate(${placedTrack.position.x}, ${placedTrack.position.y}) rotate(${placedTrack.rotation})`}
                    >
                      {track.data.anchors.map((anchor) => {
                        const isSelectedAnchor = firstAnchor?.trackIndex === index && firstAnchor?.anchorId === anchor.id;
                        
                        const isValidTarget = firstAnchor && 
                          firstAnchor.trackIndex !== index && 
                          !placedTrack.fixed;
                        
                        const isDragging = isDraggingPlaced && selectedTrackIndex !== null;
                        const isDraggedTrackAnchor = false; // Not dragged in this pass
                        
                        let connectionDepth = -1;
                        let highlightColor = 'deepskyblue';
                        
                        if (isDragging && selectedTrackIndex !== null) {
                          const connectedTracks = getConnectedTracks(selectedTrackIndex);
                          if (connectedTracks.has(index)) {
                            connectionDepth = connectedTracks.get(index)!;
                            highlightColor = connectionDepth === 0 ? 'deepskyblue' : 'yellow';
                          }
                        }
                        
                        let isDraggingMatchable = false;
                        if (isDragging && !isDraggedTrackAnchor && selectedTrackIndex !== null && connectionDepth === -1) {
                          const anchorPos = getAnchorWorldPosition(index, anchor.id);
                          const connections = anchorPos ? countAnchorConnections(anchorPos) : 0;
                          isDraggingMatchable = connections < 2;
                        }
                        
                        const anchorX = anchor.position.x;
                        const anchorY = anchor.position.y;
                        
                        const showCircle = isSelectedAnchor || isValidTarget || isDraggedTrackAnchor || isDraggingMatchable || connectionDepth >= 0;
                        
                        return (
                          <g key={anchor.id}>
                            {showCircle && (
                              <circle
                                cx={anchorX}
                                cy={anchorY}
                                r="8"
                                fill={highlightColor}
                                opacity={isDraggedTrackAnchor || isDraggingMatchable || connectionDepth >= 0 ? "0.7" : "0.5"}
                                pointerEvents="none"
                              />
                            )}
                            <path
                              d={anchor.tangent}
                              fill={isSelectedAnchor ? "yellow" : "red"}
                              stroke={isSelectedAnchor ? "orange" : "darkred"}
                              strokeWidth="0.3"
                              pointerEvents="none"
                            />
                            <path
                              d={anchor.normal}
                              fill="green"
                              stroke="darkgreen"
                              strokeWidth="0.3"
                              pointerEvents="none"
                            />
                          </g>
                        );
                      })}
                    </g>
                  );
                })}

                {/* Second pass: render dragged track's anchors on top */}
                {isDraggingPlaced && selectedTrackIndex !== null && (() => {
                  const placedTrack = placedTracks[selectedTrackIndex];
                  const track = tracks.find(t => t.id === placedTrack.trackId);
                  if (!track) return null;

                  return (
                    <g
                      key={`anchors-dragged-${selectedTrackIndex}`}
                      transform={`translate(${placedTrack.position.x}, ${placedTrack.position.y}) rotate(${placedTrack.rotation})`}
                    >
                      {track.data.anchors.map((anchor) => {
                        const isSelectedAnchor = firstAnchor?.trackIndex === selectedTrackIndex && firstAnchor?.anchorId === anchor.id;
                        const isDraggedTrackAnchor = true;
                        const connectionDepth = 0;
                        const highlightColor = 'deepskyblue';
                        
                        const anchorX = anchor.position.x;
                        const anchorY = anchor.position.y;
                        
                        const showCircle = true; // Always show for dragged track
                        
                        return (
                          <g key={anchor.id}>
                            {showCircle && (
                              <circle
                                cx={anchorX}
                                cy={anchorY}
                                r="8"
                                fill={highlightColor}
                                opacity="0.7"
                                pointerEvents="none"
                              />
                            )}
                            <path
                              d={anchor.tangent}
                              fill={isSelectedAnchor ? "yellow" : "red"}
                              stroke={isSelectedAnchor ? "orange" : "darkred"}
                              strokeWidth="0.3"
                              pointerEvents="none"
                            />
                            <path
                              d={anchor.normal}
                              fill="green"
                              stroke="darkgreen"
                              strokeWidth="0.3"
                              pointerEvents="none"
                            />
                          </g>
                        );
                      })}
                    </g>
                  );
                })()}
              </svg>
            )}
          </Box>
          
          {/* Controls info - show below canvas */}
          <Box className="mt-2">
            <Typography variant="body2" color="text.secondary">
              Right-click to lock/unlock • Shift+click to unlink • A and D keys to rotate • Double-click track to edit • Double-click anchor (red/green arrows) to snap (180° rotation)
            </Typography>
          </Box>
        </Box>
      )}

      {/* Edit Track Modal */}
      <Dialog open={isEditingTrack} onClose={() => setIsEditingTrack(false)}>
        <DialogTitle>
          {editingTrackIndex !== null && placedTracks[editingTrackIndex]?.fixed 
            ? 'Track Details (Locked)' 
            : 'Edit Track'}
        </DialogTitle>
        <DialogContent>
          <Box className="flex flex-col gap-4 mt-2">
            <TextField
              label="X Position"
              type="number"
              value={editX}
              onChange={(e) => setEditX(e.target.value)}
              fullWidth
              disabled={editingTrackIndex !== null && placedTracks[editingTrackIndex]?.fixed}
            />
            <TextField
              label="Y Position"
              type="number"
              value={editY}
              onChange={(e) => setEditY(e.target.value)}
              fullWidth
              disabled={editingTrackIndex !== null && placedTracks[editingTrackIndex]?.fixed}
            />
            <TextField
              label="Rotation (degrees)"
              type="number"
              value={editRotation}
              onChange={(e) => setEditRotation(e.target.value)}
              fullWidth
              disabled={editingTrackIndex !== null && placedTracks[editingTrackIndex]?.fixed}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={handleDeleteTrackFromModal} 
            color="error"
            disabled={editingTrackIndex !== null && placedTracks[editingTrackIndex]?.fixed}
          >
            Delete
          </Button>
          <Box sx={{ flex: 1 }} />
          <Button onClick={() => setIsEditingTrack(false)}>Cancel</Button>
          <Button 
            onClick={handleSaveTrackEdit} 
            variant="contained" 
            color="primary"
            disabled={editingTrackIndex !== null && placedTracks[editingTrackIndex]?.fixed}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Available Tracks Palette */}
      <Box>
        <Typography variant="h6" className="font-semibold mb-2">
          Available Tracks
        </Typography>
        <Box className="flex gap-3 flex-wrap">
          {tracks.map((track) => (
            <Box
              key={track.id}
              className="border border-gray-300 bg-white p-2 hover:border-blue-500"
              style={{ 
                width: 120,
                cursor: firstAnchor ? 'pointer' : 'grab'
              }}
              draggable={!firstAnchor}
              onDragStart={(e) => handleDragStart(e, track.id)}
              onClick={(e) => {
                if (firstAnchor) {
                  // Snap mode active - place and snap the track immediately
                  const newTrackData = tracks.find(t => t.id === track.id);
                  if (!newTrackData) return;

                  // Get anchor: use second anchor if Shift is held, otherwise first
                  const anchorIndex = e.shiftKey ? 1 : 0;
                  const availableAnchor = newTrackData.data.anchors[anchorIndex];

                  if (!availableAnchor) {
                    showToast(`No anchor found at index ${anchorIndex}`, 'warning');
                    return;
                  }

                  // Check if firstAnchor already has 2 connections
                  const anchorOccupancy = countAnchorConnections(firstAnchor.worldPos);
                  if (anchorOccupancy >= 2) {
                    showToast('Cannot snap: anchor already has 2 rails connected', 'warning');
                    setFirstAnchor(null);
                    return;
                  }

                  // Calculate position and rotation to align the anchor with firstAnchor (180 degrees opposite)
                  const localX = availableAnchor.position.x;
                  const localY = availableAnchor.position.y;
                  const dirX = availableAnchor.direction.x;
                  const dirY = availableAnchor.direction.y;
                  const localAngle = Math.atan2(dirY, dirX) * 180 / Math.PI;

                  // Calculate rotation needed to align with firstAnchor (180 degrees opposite)
                  const targetAngle = firstAnchor.angle + 180;
                  let angleDiff = targetAngle - localAngle;
                  
                  // Normalize angle difference to -180 to 180 range
                  if (angleDiff > 180) angleDiff -= 360;
                  if (angleDiff < -180) angleDiff += 360;
                  
                  const newRotation = angleDiff % 360;

                  // Calculate position after rotation
                  const radians = (newRotation * Math.PI) / 180;
                  const cos = Math.cos(radians);
                  const sin = Math.sin(radians);
                  const rotatedX = localX * cos - localY * sin;
                  const rotatedY = localX * sin + localY * cos;

                  // New track position = target position - rotated anchor offset
                  const newX = firstAnchor.worldPos.x - rotatedX;
                  const newY = firstAnchor.worldPos.y - rotatedY;

                  // Inherit fixed status if first track is locked
                  const firstTrack = placedTracks[firstAnchor.trackIndex];
                  const inheritFixed = firstTrack.fixed || false;

                  const newTrack: PlacedTrack = {
                    trackId: track.id,
                    position: { x: newX, y: newY },
                    rotation: newRotation,
                    fixed: inheritFixed
                  };

                  const updatedTracks = [...placedTracks, newTrack];
                  setPlacedTracks(updatedTracks);

                  // Find the remaining anchor (not the one we just connected)
                  const remainingAnchor = newTrackData.data.anchors.find(
                    anchor => anchor.id !== availableAnchor.id
                  );

                  // Calculate the world position of the remaining anchor
                  if (remainingAnchor) {
                    const remLocalX = remainingAnchor.position.x;
                    const remLocalY = remainingAnchor.position.y;
                    
                    // Apply rotation
                    const remRotatedX = remLocalX * cos - remLocalY * sin;
                    const remRotatedY = remLocalX * sin + remLocalY * cos;
                    
                    // Apply translation
                    const remWorldX = remRotatedX + newX;
                    const remWorldY = remRotatedY + newY;
                    
                    // Calculate anchor angle
                    const remDirX = remainingAnchor.direction.x;
                    const remDirY = remainingAnchor.direction.y;
                    const remLocalAngle = Math.atan2(remDirY, remDirX) * 180 / Math.PI;
                    const remWorldAngle = remLocalAngle + newRotation;

                    // Set the remaining anchor as the new firstAnchor
                    const newTrackIndex = updatedTracks.length - 1;
                    setFirstAnchor({
                      trackIndex: newTrackIndex,
                      anchorId: remainingAnchor.id,
                      worldPos: { x: remWorldX, y: remWorldY },
                      angle: remWorldAngle
                    });
                  } else {
                    // No remaining anchor, clear snap mode
                    setFirstAnchor(null);
                  }

                  // Send to server
                  if (selectedLayout) {
                    fetch('https://react.brandonfremin.com/api/layout', {
                      method: 'PUT',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        layoutId: selectedLayout.id,
                        addTrack: {
                          trackId: track.id,
                          x: newX,
                          y: newY,
                          rotation: newRotation
                        }
                      })
                    })
                    .then(response => response.json())
                    .then(data => {
                      // Update the track with the instanceId returned from server
                      if (data.instanceId) {
                        setPlacedTracks(currentTracks => {
                          const updated = [...currentTracks];
                          const trackIndex = updated.findIndex(t => 
                            t.trackId === track.id && 
                            t.position.x === newX && 
                            t.position.y === newY && 
                            !t.instanceId
                          );
                          if (trackIndex !== -1) {
                            updated[trackIndex] = {
                              ...updated[trackIndex],
                              instanceId: data.instanceId
                            };
                          }
                          return updated;
                        });

                        // If we need to set fixed status, send another request with the instanceId
                        if (inheritFixed) {
                          fetch('https://react.brandonfremin.com/api/layout', {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                              layoutId: selectedLayout.id,
                              fixTrack: {
                                instanceId: data.instanceId,
                                fixed: true
                              }
                            })
                          }).catch(error => console.error('Failed to set fixed status:', error));
                        }
                      }
                    })
                    .catch(error => console.error('Failed to update layout:', error));
                  }
                }
              }}
            >
              <Typography variant="caption" className="font-semibold block mb-1 truncate">
                {track.name}
              </Typography>
              <TrackSvg data={track.data} size={100} />
            </Box>
          ))}
        </Box>
      </Box>

      {/* Toast Notifications */}
      <Snackbar
        open={toastOpen}
        autoHideDuration={3000}
        onClose={() => setToastOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setToastOpen(false)}
          severity={toastSeverity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {toastMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
}