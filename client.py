import asyncio
import websockets
import shutil
from concurrent.futures import ThreadPoolExecutor
import winsound
import threading
from datetime import datetime


nofification_file = "notifications_alert.wav"

def play_notification_sound():
   # winsound.PlaySound(nofification_file, winsound.SND_FILENAME)
    threading.Thread(target=winsound.PlaySound, args=(nofification_file, winsound.SND_FILENAME)).start()

def get_input(prompt):
    return input(prompt)

def get_time():
    return datetime.now().strftime("%H:%M")

async def receive_messages(websocket):
    try:
        while True:
            message = await websocket.recv()
            parts_of_message = message.split(' ', 1)
            if parts_of_message[1] == "has left the room" or "was removed from the room by" in message:
                formatted_message = format_message(message, 'red', False, False)
            elif parts_of_message[1] == "has joined the room"  or "is an admin now!" in message:
                formatted_message = format_message(message, 'green', False, False)
            else:
                formatted_message = format_message(message)
                if not message.startswith("[History]"):
                    play_notification_sound()
            #message_time = get_time()
            print(f"{formatted_message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by the server")

async def send_messages(websocket):
  #  with ThreadPoolExecutor(1, "thread_for_input") as pool:
        try:
            while True:
                # Get message input from the user
                message = await asyncio.to_thread(input, "")
                #message = await asyncio.get_event_loop().run_in_executor(pool, get_input, "")
                await websocket.send(message)
                if message == "logout":
                    break

        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by the server.")

def format_message(message, color='green', bold=False, center=True):
    
    # Get terminal width
    terminal_width = shutil.get_terminal_size().columns

    colors = {
        'green': '\033[32m',
        'red': '\033[31m',
        'reset': '\033[0m'
    }

    bold_code = '\033[1m' if bold else ''
    color_code = colors.get(color, colors['reset'])  # Default to reset if color not found
    
    # Format the message with the chosen color and style
    styled_message = f"{bold_code}{color_code}{message}{colors['reset']}"

    if center:
        centered_message = styled_message.center(terminal_width)
        return centered_message
    else:
        return styled_message



async def authenticate(websocket):
   # with ThreadPoolExecutor(1, "thread_for_input") as pool:
        try:

            while True:
                # ask for an action
                #action = await asyncio.get_event_loop().run_in_executor(pool, get_input, "Hi! do you want to login or register? ")
                action = await asyncio.to_thread(input, "Hi! Do you want to login or register? ")
                await websocket.send(action)
                response = await websocket.recv()
                if response == "Please write only login or register!":
                    print(response)
                else:
                    print(response)
                    break
            # Ask for username and send it to the server
            #username = await asyncio.get_event_loop().run_in_executor(pool, get_input, "Enter your username: ")
            username = await asyncio.to_thread(input, "Enter your username: ")
            await websocket.send(username)

            # Ask for password and send it to the server
            #password = await asyncio.get_event_loop().run_in_executor(pool, get_input, "Enter your password: ")
            password = await asyncio.to_thread(input, "Enter your password: ")
            await websocket.send(password)

            # Receive authentication response from the server
            auth_response = await websocket.recv()
            if auth_response.startswith("JWT"):
                print("Authentication successful.")
                print(f"Received token: {auth_response}")
                return True
            else:
                print(auth_response)
                return False # Exit if authentication fails
            
            
            
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by the server.")



async def chat_client():
    uri = "ws://localhost:12345"
    async with websockets.connect(uri) as websocket:
         # Create tasks for sending and receiving messages
        if not await authenticate(websocket):
            return  # Exit if authentication fails

        #room = input("What room you want to join to / to create?  / if you wish to pm to someone please write pm and then the user id:\n")
        #await websocket.send(room)
        

        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket))
        
        # Wait until both tasks are done
        await asyncio.gather(receive_task, send_task)


if __name__ == "__main__":
    asyncio.run(chat_client()) 
