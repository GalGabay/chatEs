import asyncio
import websockets
import jwt

SECRET_KEY = "my_secret_key"

users = set()

USER_DATABASE = {
    "gal": "5250",
    "yuval": "5250"
}

async def connection(websocket):
    if not await authenticate(websocket):
        return  # Close the connection if authentication fails
    

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

async def authenticate(websocket):
    try:
        # Receive the authentication data (username and password)
        username = await websocket.recv()
        password = await websocket.recv()
        
        # Check username and password
        if USER_DATABASE.get(username) == password:
            # Generate JWT token
            token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
            await websocket.send(f"JWT {token}")
            return True
        else:
            await websocket.send("Authentication failed")
            return False
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

async def main():
    start_server = await websockets.serve(connection, "localhost", 12345)
    print("Server is running on ws://localhost:12345")
    await start_server.wait_closed()  # Keeps the server running

if __name__ == "__main__":
    asyncio.run(main())