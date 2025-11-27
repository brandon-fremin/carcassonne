
import { useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { setPingState } from '../redux/pingReducer';
import type { PingState, PingType } from '../redux/pingReducer';

// Map to store one WebSocket per URL
const wsMap: Map<string, WebSocket> = new Map();
const clientCountMap: Map<string, number> = new Map();

async function pingHttp(setHttp: (status: PingType) => void, attempts: number = 0) {
  const response = await fetch("https://react.brandonfremin.com/api/ping");
  if (response.ok) {
    setHttp("OK");
    console.log(`Connected to HTTP service.`, await response.json());
  } else if (attempts >= 0) {
    console.log(`Retrying in 5 seconds... (${attempts + 1} attempts left)`);
    setTimeout(() => pingHttp(setHttp, attempts - 1), 5000);
  } else {
    console.log(`Failed to connect to HTTP service.`);
    setHttp("FAIL");
  }
}

function getWebsocket(url: string): WebSocket {
    let ws = wsMap.get(url);
    if (!ws || ws.readyState === WebSocket.CLOSED) {
        ws = new WebSocket(url);
        wsMap.set(url, ws);
    }
    return ws;
}

export function useWebSocket(url: string) {
    const dispatch = useDispatch();
    const wsRef = useRef<WebSocket | null>(null);
    const messageQueueRef = useRef<string[]>([]);

    useEffect(() => {
        // Get or create the WebSocket connection for this URL
        const ws = getWebsocket(url);
        wsRef.current = ws;
        // Increment client count for this URL
        clientCountMap.set(url, (clientCountMap.get(url) || 0) + 1);

        ws.onopen = () => {
            dispatch(setPingState({ ws: "OK" }));
            console.log(`[WebSocket] Connected: ${url}`);

            // Process any queued messages
            while (messageQueueRef.current.length > 0) {
                const message = messageQueueRef.current.shift();
                if (message) ws.send(message);
            }
        };

        ws.onmessage = (event) => {
            console.log(event)
            try {
                const data = JSON.parse(event.data);
                console.log(`[WebSocket] Parsed:`, data);
                if (data.heartbeat) {
                    console.log("Got heartbeat:", data);
                    dispatch(setPingState(data.heartbeat as PingState));
                }
            } catch {
                console.warn("Non-JSON message:", event.data);
            }
        };

        ws.onclose = () => {
            dispatch(setPingState({ ws: "FAIL" }));
            console.log(`[WebSocket] Disconnected: ${url}`);
        };

        ws.onerror = (err) => {
            dispatch(setPingState({ ws: "FAIL" }));
            console.error(`[WebSocket] Error: ${url}`, err);
        };

        return () => {
            // Decrement client count for this URL
            const count = (clientCountMap.get(url) || 1) - 1;
            if (count <= 0) {
                // Last client for this URL, close and clean up
                if (ws.readyState === WebSocket.OPEN) {
                    ws.close();
                }
                wsMap.delete(url);
                clientCountMap.delete(url);
            } else {
                clientCountMap.set(url, count);
            }
        };
    }, [url, dispatch]);

    const setHttp = (status: PingType) => {
        dispatch(setPingState({ http: status }));
    };
    useEffect(() => {
        pingHttp(setHttp, 5);
    }, []);

    // return helper to send messages
    const sendMessage = (message: string) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            // Queue the message if we don't have a valid connection
            messageQueueRef.current.push(message);
            return;
        }
        ws.send(message);
    };

    return { sendMessage };
}