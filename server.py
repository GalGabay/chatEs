import asyncio
import websockets

users = set()

async def connection(websocket):
    users.add(websocket) # add the new client to the list of connected users
    try:
        async for message in websocket:
            print(f"Server received: {message}")
            # Broadcast the received message to all connected users
            await asyncio.gather(*(user.send(message) for user in users)) # why gather and not wait?
           # await websocket.send(f"Received your message: {message}")
    except websockets.ConnectionClosedOK:
        print("Connection closed")
    finally:
        users.remove(websocket)

async def main():
    start_server = await websockets.serve(connection, "localhost", 12345)
    print("Server is running on ws://localhost:12345")
    await start_server.wait_closed()  # Keeps the server running

if __name__ == "__main__":
    asyncio.run(main())