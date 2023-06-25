import { useDispatch, useSelector } from 'react-redux';
import React, { useState } from 'react'
import { ACTIONS } from '../state/reducer'

function request(data = {}) {
  return {
    method: "PUT",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }
}

function Component({component, tiles, dispatch, selectedComponentId}) {
  const key = `${component?.id} (${component?.type} - ${component.includedTileIds.length})`
  const onClick = () => {
    console.log(`Selecting Component ${key}`)
    dispatch({
      type: ACTIONS.SELECT_COMPONENT,
      payload: { componentId: component?.id }
    })
  }
  return (
    <button
      style={{
        width: "80%"
      }}
      disabled={selectedComponentId === component?.id}
      onClick={onClick}
    >
      {key}
    </button>
  )
}

export default function Components() {
  const dispatch = useDispatch();

  const tiles = useSelector((state) => state?.game?.board?.tiles)
  const components = useSelector((state) => state?.game?.board?.components)
  const selectedComponentId = useSelector((state) => state?.selectedComponentId)

  if (components === undefined) {
    return (
      <div>
        No Components Loaded
      </div>
    )
  }

  return (
    <div style={{
      display: "flex", 
      flexDirection: "column",
      alignItems: "center",
      gap: 2
    }}>
      {Object.entries(components).map(([key, value]) => 
        <Component 
          key={key}
          component={value} 
          tiles={tiles} 
          dispatch={dispatch} 
          selectedComponentId={selectedComponentId} 
        />)
      }
    </div>
  )
}