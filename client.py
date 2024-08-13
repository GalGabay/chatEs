import asyncio
import websockets

async def receive_messages(websocket):
    try:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by the server.")

async def send_messages(websocket):
    try:
        while True:
            message = input("what is your name: ")
            await websocket.send(message)
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by the server.")


async def chat_client():
    uri = "ws://localhost:12345"
    async with websockets.connect(uri) as websocket:
         # Create tasks for sending and receiving messages
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket))
        
        # Wait until both tasks are done
        await asyncio.gather(receive_task, send_task)


if __name__ == "__main__":
    asyncio.run(chat_client()) 
