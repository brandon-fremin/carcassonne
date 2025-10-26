import asyncio, websockets, os

CF_ACCESS_CLIENT_ID: str = os.environ.get("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET: str = os.environ.get("CF_ACCESS_CLIENT_SECRET")

async def connect(uri: str, headers: dict):
    async with websockets.connect(uri, additional_headers=headers) as websocket:
        print("Connected to WebSocket server")

        # Send a message
        await websocket.send("Hello from client!")
        print("Sent: Hello from client!")

        # Receive echo from server
        response = await websocket.recv()
        print(f"Received: {response}")
        
        # Optionally, keep talking in a loop
        while True:
            message = input("Type message to send (or 'exit'): ")
            if message.lower() == "exit":
                break
            await websocket.send(message)
            echo = await websocket.recv()
            print(f"Echo: {echo}")

        await websocket.close()

# uri = "ws://localhost:8000/ping"  # Adjust if hosted elsewhere
# asyncio.run(connect(uri, {}))

# uri = "ws://planned-calendars-eyes-andrews.trycloudflare.com/ping"  # Adjust if hosted elsewhere
# asyncio.run(connect(uri, {}))

uri = f"wss://iot.brandonfremin.com/ping"  # Adjust if hosted elsewhere
headers = {
    "CF-Access-Client-Id": CF_ACCESS_CLIENT_ID,
    "CF-Access-Client-Secret": CF_ACCESS_CLIENT_SECRET
}
asyncio.run(connect(uri, headers))