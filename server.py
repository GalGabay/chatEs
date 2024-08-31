from dotenv import load_dotenv
import os
from datetime import datetime
import asyncio
import websockets
import jwt
from db import (
    find_user_by_username,
    insert_room,
    delete_room,
    add_user,
    delete_user,
    room_exists_by_name,
    add_user_to_room,
    remove_user_from_room,
    get_users_in_room,
    remove_user_from_rooms,
    add_room_to_user,
    get_num_of_rooms,
    get_num_of_users,
    remove_room_from_user, 
    find_user_by_id,
    add_message,
    get_message_history
)



#users = set()
#rooms = {}

#USER_DATABASE = {
 #   "gal": "5250",
 #   "yuval": "5250",
 #   "bony": "5250"
#}

# DB:
#MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
#client = MongoClient(MONGO_URI)
#db = client["chatSportsDB"]
#users = db["users"]
#rooms = db["rooms"]

#async def find_user(username):
#    return users.find_one({"username": username})

# Global dictionary to map users to their WebSocket connections

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

websocket_to_username = {}
username_to_websocket = {}


async def connection(websocket):

    if not await authenticate(websocket):
        return  # Close the connection if authentication fails
    
    #users.add(websocket) # add the new client to the list of connected users

    # add the user to the room he asked for
   # try:
    #    room_name = await websocket.recv()
    #except websockets.ConnectionClosedError as e:
    #    print(f"Connection closed unexpectedly: {e}")
    #    return
   
   # await join_room(room_name, websocket)    
    try:
        async for message in websocket:
            print(f"Server received: {message}")
            await handle_message(message, websocket)
            
    except websockets.ConnectionClosedOK:
        print("Connection closed")
    finally:
        await handle_logout(websocket)       

async def authenticate(websocket):
    try:
        while True:
            action = await websocket.recv()
            if action.lower() == "login":
                await websocket.send("Please Log In:")
                break
            elif action.lower() == "register":
                await websocket.send("Please Register:")
                break
            await websocket.send("Please write only login or register!")


        # Receive the authentication data (username and password)
        username = await websocket.recv()
        password = await websocket.recv()

        if action == "login":
            return await handle_login(websocket, username, password)
        
        elif action == "register":
            return await handle_register(websocket, username, password)

        return False
    #else:
       # await websocket.send("Authentication failed")
        #return False
    except Exception as e:
        print(f"Authentication error: {e}")
        return False
    
async def handle_login(websocket, username,password):
    user = find_user_by_username(username)

    # Check if the user is already logged in
    if username in username_to_websocket:
        await websocket.send("User already logged in")
        return False
    
    # check if the password is incorrect
    if user and user["password"] != password: # if user exists and password is incorrect
        await websocket.send("Authentication failed")
        return False

    # check if user doesn't exist
    if not user: 
        await websocket.send("User doesn't exist! Please register first")
        return False
    
    websocket_to_username[websocket] = username
    username_to_websocket[username] = websocket

    # Generate JWT token
    token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
    await websocket.send(f"JWT {token}")
    return True

async def handle_register(websocket, username, password):
    user = find_user_by_username(username)

    # if username is already used
    if user:
        await websocket.send("Username already taken")
        return False
    
# creating the user using the user schema
    users_count = get_num_of_users()
    user_to_add = {
        "id": users_count + 1,
        "username": username,
        "password": password,
        "rooms": []
    }
    add_user(user_to_add)
    websocket_to_username[websocket] = username
    username_to_websocket[username] = websocket

    # Generate JWT token
    token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
    await websocket.send(f"JWT {token}")
    return True
    
async def join_room(room_name, websocket):
     #room_name = await websocket.recv()
    role = "member"
    room = room_exists_by_name(room_name) # checks if there is a room with this name
    if not room:
        room_count = get_num_of_rooms()
        room = {
        "name": room_name,
        "id": room_count + 1,
        "users": []
        }
        insert_room(room)
        role = "admin"

    user_name = websocket_to_username[websocket]
    user = find_user_by_username(user_name)
    user_to_room = {
        "id": user["id"],
        "username": user["username"],
        "role": role
    }
    add_user_to_room(room, user_to_room)
    add_room_to_user(user,room)

    messages = get_message_history(room_name)

    for message in reversed(list(messages)):
        await websocket.send(f"[History] {message['username']}: {message['message']}")


    #if room not in rooms["name"]:
    #    rooms[room] = set()
   # rooms[room].add(websocket)

async def save_message(message, room_name, username):
    new_message = {
        "room_name": room_name,
        "username": username,
        "message": message,
        "time": datetime.now()
    }
    add_message(new_message)

async def handle_message(message, websocket):

    if message.startswith("leave"): # leave a room
        await leave_room(message, websocket)
    elif message.startswith("join"): # join a room
        words = message.split()
        room_name = ' '.join(words[1:])
        await join_room(room_name, websocket)
        room = room_exists_by_name(room_name)
        await broadcast_message("join", room, websocket)
    elif message.startswith("pm"): # pm someone
        await handle_private_message(message, websocket)
    elif message.startswith("logout"): # user wants to logout
        await handle_logout(websocket)
    else: # send a message to room
        room_name = message.split()[0]
        room = room_exists_by_name(room_name)
        if room:
            # Broadcast the received message to all connected users
            words = message.split()
            message_to_send = ' '.join(words[1:])
            await save_message(' '.join(words[1:]), room_name, websocket_to_username[websocket]) # save the message in the db
            await broadcast_message(message_to_send, room, websocket)
        
        #await asyncio.gather(*(username_to_websocket[find_user_by_id(user_id)["username"]].send(message) for user_id in get_users_in_room(room))) # why gather and not wait?
    # await websocket.send(f"Received your message: {message}")

async def broadcast_message(message, room, websocket):
    username = websocket_to_username[websocket]
    users_in_room = get_users_in_room(room)
    for user_id in users_in_room:
        username_to_send = find_user_by_id(user_id)["username"]
        socket_to_send = username_to_websocket.get(username_to_send)
        if socket_to_send:
            if message.startswith("leave"):
                await socket_to_send.send(f"{username} has left the room")
            elif message == "join":
                await socket_to_send.send(f"{username} has joined the room")
            else:
                await socket_to_send.send(f"{username} sent in {room["name"]}: {message}")

async def leave_room(message, websocket):
    room_name_to_leave = message[len("leave"):].strip()
    room_to_leave = room_exists_by_name(room_name_to_leave)
    if room_to_leave:
        user_name = websocket_to_username[websocket]
        user = find_user_by_username(user_name)
        remove_user_from_room(room_to_leave, user)
        remove_room_from_user(user_name,room_to_leave)
    await broadcast_message(message, room_to_leave, websocket)

async def handle_private_message(message, websocket):
    parts = message.split(' ', 2)
    username_to_send = parts[1]
    message_to_send = parts[2]
    await save_message(message_to_send,username_to_send, websocket_to_username[websocket]) # save the message in the db
    if username_to_send in username_to_websocket:
        websocket_to_send = username_to_websocket[username_to_send]
        sender_username = websocket_to_username[websocket]
        await websocket_to_send.send(f"{sender_username} sent in PM: {message_to_send}")
    else:
        await websocket.send(f"User {username_to_send} is not online.")

# currently it is not in use
async def cleanup_user(websocket):
    username = websocket_to_username[websocket]
    user = find_user_by_username(username)
    remove_user_from_rooms(user)
    user = find_user_by_username(username)
    delete_user(user)
    #delete the connections:
    if websocket in websocket_to_username:
        username = websocket_to_username.pop(websocket)
        if username in username_to_websocket:
            username_to_websocket.pop(username)
    #rooms[room].remove(websocket)
    # if not rooms[room]:
    #    del rooms[room]   

async def handle_logout(websocket):
    username = websocket_to_username.get(websocket)

    if username:

        websocket_to_username.pop(websocket, None)
        username_to_websocket.pop(username, None)

        print(f"{username} has logged out.")

    # Close the WebSocket connection
    await websocket.close()




async def main():
    start_server = await websockets.serve(connection, "localhost", 12345)
    print("Server is running on ws://localhost:12345")
    await start_server.wait_closed()  # Keeps the server running

if __name__ == "__main__":
    asyncio.run(main())