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
    type: string;
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
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
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
    type: string;
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
      const tracks = selectedLayout.data?.tracks?.map(track => ({
        instanceId: track.instanceId,
        trackId: track.trackId,
        position: { x: track.x, y: track.y },
        rotation: track.rotation,
        fixed: track.fixed || false
      })) || [];
      setPlacedTracks(tracks);
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

      // Find the first anchor with opposite gender
      const oppositeGenderAnchor = newTrackData.data.anchors.find(
        anchor => anchor.type !== firstAnchor.type
      );

      if (!oppositeGenderAnchor) {
        showToast('No compatible anchor found on this track', 'warning');
        return;
      }

      // Check if firstAnchor already has 2 connections
      const anchorOccupancy = countAnchorConnections(firstAnchor.worldPos);
      if (anchorOccupancy >= 2) {
        showToast('Cannot snap: anchor already has 2 rails connected', 'warning');
        setFirstAnchor(null);
        return;
      }

      // Calculate position and rotation to align the opposite gender anchor with firstAnchor
      // Start with the anchor's local position and direction
      const localX = oppositeGenderAnchor.position.x;
      const localY = oppositeGenderAnchor.position.y;
      const dirX = oppositeGenderAnchor.direction.x;
      const dirY = oppositeGenderAnchor.direction.y;
      const localAngle = Math.atan2(dirY, dirX) * 180 / Math.PI;

      // Calculate rotation needed to align with firstAnchor
      const targetAngle = firstAnchor.angle;
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
        trackId,
        position: { x: newX, y: newY },
        rotation: newRotation,
        fixed: inheritFixed
      };

      const updatedTracks = [...placedTracks, newTrack];
      setPlacedTracks(updatedTracks);

      // Update canvas size
      updateCanvasSize(updatedTracks);

      // Find the remaining anchor (not the one we just connected)
      const remainingAnchor = newTrackData.data.anchors.find(
        anchor => anchor.id !== oppositeGenderAnchor.id
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
          angle: remWorldAngle,
          type: remainingAnchor.type
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
              trackId,
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
                t.trackId === trackId && 
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
    
    const placedTrack = placedTracks[index];

    // Don't allow dragging fixed tracks
    if (placedTrack.fixed) {
      return;
    }

    const track = tracks.find(t => t.id === placedTrack.trackId);
    if (!track) return;

    setSelectedTrackIndex(index);
    setIsDraggingPlaced(true);

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

    const updatedTracks = [...placedTracks];
    updatedTracks[selectedTrackIndex] = {
      ...updatedTracks[selectedTrackIndex],
      position: { x: newX, y: newY }
    };
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
      // First anchor selected - store type info
      setFirstAnchor({
        trackIndex,
        anchorId,
        worldPos: anchorPos,
        angle: anchorPos.angle,
        type: anchor.type
      });
    } else {
      // Second anchor selected - perform snap
      
      // Rule 3: Only male and female anchors can connect
      if (firstAnchor.type === anchor.type) {
        console.log('Cannot snap: same anchor types (need male-female connection)');
        showToast('Cannot snap: anchors must be male-female pairs', 'warning');
        setFirstAnchor(null);
        return;
      }
      
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

      // Calculate the transformation needed
      // The second anchor should align with the first anchor (same direction)
      const targetAngle = firstAnchor.angle;
      const angleDiff = targetAngle - anchorPos.angle;
      
      // Normalize angle difference to -180 to 180 range
      let normalizedAngleDiff = angleDiff % 360;
      if (normalizedAngleDiff > 180) normalizedAngleDiff -= 360;
      if (normalizedAngleDiff < -180) normalizedAngleDiff += 360;
      
      const newRotation = (placedTrack.rotation + normalizedAngleDiff) % 360;

      // Calculate new position so the anchor ends up at firstAnchor position
      // We need to rotate the anchor's local position by the new rotation
      // (anchor is already defined above)

      const localX = anchor.position.x;
      const localY = anchor.position.y;

      // Apply new rotation to anchor position
      const radians = (newRotation * Math.PI) / 180;
      const cos = Math.cos(radians);
      const sin = Math.sin(radians);
      const rotatedX = localX * cos - localY * sin;
      const rotatedY = localX * sin + localY * cos;

      // New track position = target position - rotated anchor offset
      const newX = firstAnchor.worldPos.x - rotatedX;
      const newY = firstAnchor.worldPos.y - rotatedY;

      // Rule 3: If first track is fixed, second track becomes fixed too
      const firstTrack = placedTracks[firstAnchor.trackIndex];
      const inheritFixed = firstTrack.fixed || false;
      
      // Update track
      setPlacedTracks(currentTracks =>
        currentTracks.map((t, i) =>
          i === trackIndex ? { ...t, position: { x: newX, y: newY }, rotation: newRotation, fixed: inheritFixed } : t
        )
      );

      // Send to server
      if (placedTrack.instanceId && selectedLayout) {
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
              rotation: newRotation
            },
            ...(inheritFixed && {
              fixTrack: {
                instanceId: placedTrack.instanceId,
                fixed: true
              }
            })
          })
        }).catch(error => console.error('Failed to update track:', error));
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
          angle: anchorPos.angle,
          type: anchor.type
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

    // Update local state
    setPlacedTracks(currentTracks => 
      currentTracks.map((t, i) => 
        i === editingTrackIndex ? { 
          ...t, 
          position: { x: newX, y: newY },
          rotation: newRotation % 360
        } : t
      )
    );

    // Send to server if track has instanceId
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

    // Update local state immediately
    setPlacedTracks(currentTracks => 
      currentTracks.map((t, i) => 
        i === index ? { ...t, rotation: newRotation } : t
      )
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
              // Only connect opposite genders
              if (draggedAnchor.type === otherAnchor.type) return;

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

              console.log(`Checking: ${draggedAnchor.id} (${draggedAnchor.type}) to ${otherAnchor.id} (${otherAnchor.type}), distance: ${distance.toFixed(1)}`);

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
          const targetAnchorPos = getAnchorWorldPosition(bestSnap.targetTrackIndex, bestSnap.targetAnchorId);
          const draggedAnchor = draggedTrackData.data.anchors.find(a => a.id === bestSnap.draggedAnchorId);

          if (targetAnchorPos && draggedAnchor) {
            // Calculate snap transformation
            const localX = draggedAnchor.position.x;
            const localY = draggedAnchor.position.y;
            const dirX = draggedAnchor.direction.x;
            const dirY = draggedAnchor.direction.y;
            const localAngle = Math.atan2(dirY, dirX) * 180 / Math.PI;
            
            // Calculate current world angle of the dragged anchor
            const currentWorldAngle = localAngle + draggedTrack.rotation;

            const targetAngle = targetAnchorPos.angle;
            let angleDiff = targetAngle - currentWorldAngle;
            
            if (angleDiff > 180) angleDiff -= 360;
            if (angleDiff < -180) angleDiff += 360;
            
            const newRotation = (draggedTrack.rotation + angleDiff) % 360;

            const radians = (newRotation * Math.PI) / 180;
            const cos = Math.cos(radians);
            const sin = Math.sin(radians);
            const rotatedX = localX * cos - localY * sin;
            const rotatedY = localX * sin + localY * cos;

            const newX = targetAnchorPos.x - rotatedX;
            const newY = targetAnchorPos.y - rotatedY;

            // Inherit fixed status if target is locked
            const inheritFixed = targetTrack.fixed || false;

            // Update track position and rotation
            setPlacedTracks(currentTracks =>
              currentTracks.map((t, i) =>
                i === selectedTrackIndex ? { ...t, position: { x: newX, y: newY }, rotation: newRotation, fixed: inheritFixed } : t
              )
            );

            // Send to server
            if (draggedTrack.instanceId && selectedLayout) {
              fetch('https://react.brandonfremin.com/api/layout', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  layoutId: selectedLayout.id,
                  addTrack: {
                    instanceId: draggedTrack.instanceId,
                    trackId: draggedTrack.trackId,
                    x: newX,
                    y: newY,
                    rotation: newRotation
                  },
                  ...(inheritFixed && {
                    fixTrack: {
                      instanceId: draggedTrack.instanceId,
                      fixed: true
                    }
                  })
                })
              }).catch(error => console.error('Failed to update track:', error));
            }

            setIsDraggingPlaced(false);
            setSelectedTrackIndex(null);
            return;
          }
        }
      }

      // No snap found, just save the current position
      const placedTrack = placedTracks[selectedTrackIndex];

      // Send to server to update layout
      if (selectedLayout) {
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

    setIsDraggingPlaced(false);
    setSelectedTrackIndex(null);
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

                      {/* Anchors */}
                      {track.data.anchors.map((anchor) => {
                        const isSelectedAnchor = firstAnchor?.trackIndex === index && firstAnchor?.anchorId === anchor.id;
                        
                        // Check if this anchor is a valid snap target (opposite gender from selected)
                        const isValidTarget = firstAnchor && 
                          firstAnchor.trackIndex !== index && 
                          firstAnchor.type !== anchor.type && 
                          !placedTrack.fixed;
                        
                        // Check if we're dragging and this is a matchable anchor
                        const isDragging = isDraggingPlaced && selectedTrackIndex !== null;
                        const isDraggedTrackAnchor = isDragging && selectedTrackIndex === index;
                        
                        let isDraggingMatchable = false;
                        if (isDragging && !isDraggedTrackAnchor && selectedTrackIndex !== null) {
                          const draggedTrack = placedTracks[selectedTrackIndex];
                          const draggedTrackData = tracks.find(t => t.id === draggedTrack.trackId);
                          
                          if (draggedTrackData) {
                            // Check if this anchor has opposite gender from any anchor on dragged track
                            const hasOppositeGender = draggedTrackData.data.anchors.some(
                              draggedAnchor => draggedAnchor.type !== anchor.type
                            );
                            
                            // Check if not fully connected
                            const anchorPos = getAnchorWorldPosition(index, anchor.id);
                            const connections = anchorPos ? countAnchorConnections(anchorPos) : 0;
                            
                            isDraggingMatchable = hasOppositeGender && connections < 2;
                          }
                        }
                        
                        // Determine highlight color based on gender
                        const isMale = anchor.type === 'male';
                        const highlightColor = isMale ? 'dodgerblue' : 'hotpink';
                        
                        // Use the explicit position data from the anchor
                        const anchorX = anchor.position.x;
                        const anchorY = anchor.position.y;
                        
                        // Show anchor circle if: it's selected OR (snap mode active and it's a valid target) OR (dragging and matchable)
                        const showCircle = isSelectedAnchor || isValidTarget || isDraggedTrackAnchor || isDraggingMatchable;
                        
                        return (
                          <g key={anchor.id}>
                            {/* Colored circle based on gender */}
                            {showCircle && (
                              <circle
                                cx={anchorX}
                                cy={anchorY}
                                r="8"
                                fill={highlightColor}
                                opacity={isDraggedTrackAnchor || isDraggingMatchable ? "0.7" : "0.5"}
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
              </svg>
            )}
          </Box>
          
          {/* Controls info - show below canvas */}
          <Box className="mt-2">
            <Typography variant="body2" color="text.secondary">
              Right-click to lock/unlock • A and D keys to rotate • Double-click track to edit • Double-click anchor (red/green arrows) to snap
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
              onClick={() => {
                if (firstAnchor) {
                  // Snap mode active - place and snap the track immediately
                  const newTrackData = tracks.find(t => t.id === track.id);
                  if (!newTrackData) return;

                  // Find the first anchor with opposite gender
                  const oppositeGenderAnchor = newTrackData.data.anchors.find(
                    anchor => anchor.type !== firstAnchor.type
                  );

                  if (!oppositeGenderAnchor) {
                    showToast('No compatible anchor found on this track', 'warning');
                    return;
                  }

                  // Check if firstAnchor already has 2 connections
                  const anchorOccupancy = countAnchorConnections(firstAnchor.worldPos);
                  if (anchorOccupancy >= 2) {
                    showToast('Cannot snap: anchor already has 2 rails connected', 'warning');
                    setFirstAnchor(null);
                    return;
                  }

                  // Calculate position and rotation to align the opposite gender anchor with firstAnchor
                  const localX = oppositeGenderAnchor.position.x;
                  const localY = oppositeGenderAnchor.position.y;
                  const dirX = oppositeGenderAnchor.direction.x;
                  const dirY = oppositeGenderAnchor.direction.y;
                  const localAngle = Math.atan2(dirY, dirX) * 180 / Math.PI;

                  // Calculate rotation needed to align with firstAnchor
                  const targetAngle = firstAnchor.angle;
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
                    anchor => anchor.id !== oppositeGenderAnchor.id
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
                      angle: remWorldAngle,
                      type: remainingAnchor.type
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