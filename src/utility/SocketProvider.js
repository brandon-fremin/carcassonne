import React, { useContext, useEffect, useState } from 'react'
import io from 'socket.io-client'

const SocketContext = React.createContext()

export function useSocket() {
  return useContext(SocketContext)
}

// const socket = io("http://localhost:5000")

export function SocketProvider({ id, children }) {
  const [socket, setSocket] = useState()

  useEffect(() => {
    const newSocket = io(
      'http://localhost:3000',
      {
        cors: {
          origin: ['http://localhost:5000']
        }
      }
    )
    setSocket(newSocket)

    return () => {
      if (socket) { // <-- This is important
        newSocket.close()
      }
    }
  }, [id])

  return (
    <SocketContext.Provider value={socket}>
      {children}
    </SocketContext.Provider>
  )
}