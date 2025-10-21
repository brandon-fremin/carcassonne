import './App.css';
import React, { useEffect } from 'react'
import TileList from './TileList';
// import { SocketProvider, useSocket } from './utility/SocketProvider';
import io from 'socket.io-client'

const socket = io.connect("ws://localhost:5000")

socket.on('connection', (s) => {
  console.log(`⚡: ${s.id} user just connected!`);

  //Listens and logs the message to the console
  s.on('message', (data) => {
    console.log(data);
  });

  s.on('disconnect', () => {
    console.log('🔥: A user disconnected');
  });
})

// const socket = io("http://localhost:5000")

// socket.onAny((eventName, args) => {
//   console.log(`${eventName}: ${JSON.stringify(args)}`);
// });

function Test() {
  // const socket = useSocket();

  const callback = () => {
    console.log("Hello World")
  }

  // useEffect(() => {
  //   if (socket == null) return
  //   socket.on('message', callback)
  //   return () => socket.off('message')
  // }, [socket])

  const handleClick = () => {
    console.log("handleClick")
    // console.log(socket)
    // socket.emit('handleClick', { "hello": "world" })
  }

  return (
    // <SocketProvider>
    <button onClick={handleClick}>
      Click Me
    </button>
    // </SocketProvider>
  )
}

function App() {
  return (
    <div>
      <Test />
      <TileList />
    </div>
  );
}

export default App;

