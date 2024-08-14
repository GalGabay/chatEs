import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor

def get_input(prompt):
    return input(prompt)

async def receive_messages(websocket):
    try:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}\n")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by the server.")

async def send_messages(websocket):
    with ThreadPoolExecutor(1, "thread_for_input") as pool:
        try:
            while True:
                # Get message input from the user
                message = await asyncio.get_event_loop().run_in_executor(pool, get_input, "Enter message: ")
                await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by the server.")


async def authenticate(websocket):
    with ThreadPoolExecutor(1, "thread_for_input") as pool:
        try:
            # Ask for username and send it to the server
            username = await asyncio.get_event_loop().run_in_executor(pool, get_input, "Enter your username: ")
            await websocket.send(username)

            # Ask for password and send it to the server
            password = await asyncio.get_event_loop().run_in_executor(pool, get_input, "Enter your password: ")
            await websocket.send(password)

            # Receive authentication response from the server
            auth_response = await websocket.recv()
            if auth_response.startswith("JWT"):
                print("Authentication successful.")
                print(f"Received token: {auth_response}")
                return True
            else:
                print("Authentication failed.")
                return False # Exit if authentication fails
            
            
            
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by the server.")



async def chat_client():
    uri = "ws://localhost:12345"
    async with websockets.connect(uri) as websocket:
         # Create tasks for sending and receiving messages
        if not await authenticate(websocket):
            return  # Exit if authentication fails
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket))
        
        # Wait until both tasks are done
        await asyncio.gather(receive_task, send_task)


if __name__ == "__main__":
    asyncio.run(chat_client()) 
