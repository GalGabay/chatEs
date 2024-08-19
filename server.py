from dotenv import load_dotenv
import os
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
    get_num_of_users
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
    try:
        room_name = await websocket.recv()
    except websockets.ConnectionClosedError as e:
        print(f"Connection closed unexpectedly: {e}")
        return
    #room_name = await websocket.recv()
    room = room_exists_by_name(room_name) # checks if there is a room with this name
    if not room:
        room_count = get_num_of_rooms()
        room = {
        "name": room_name,
        "id": room_count + 1,
        "users": []
        }
        insert_room(room)

    user_name = websocket_to_username[websocket]
    user = find_user_by_username(user_name)
    add_user_to_room(room, user)
    add_room_to_user(user,room)
    #if room not in rooms["name"]:
    #    rooms[room] = set()
   # rooms[room].add(websocket)

    try:
        async for message in websocket:
            print(f"Server received: {message}")

            # Broadcast the received message to all connected users
            await asyncio.gather(*(username_to_websocket[user["username"]].send(message) for user in get_users_in_room(room))) # why gather and not wait?
           # await websocket.send(f"Received your message: {message}")
    except websockets.ConnectionClosedOK:
        print("Connection closed")
    finally:
        delete_user(user)
        remove_user_from_rooms(user) # ?? i want to remove the user from all rooms
        if get_users_in_room(room) == []:
            delete_room(room)
        #delete the connections:
        if websocket in websocket_to_username:
            username = websocket_to_username.pop(websocket)
            if username in username_to_websocket:
                username_to_websocket.pop(username)
        #rooms[room].remove(websocket)
       # if not rooms[room]:
        #    del rooms[room]

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
        
        elif action == "register":
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
    #else:
       # await websocket.send("Authentication failed")
        #return False
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

async def main():
    start_server = await websockets.serve(connection, "localhost", 12345)
    print("Server is running on ws://localhost:12345")
    await start_server.wait_closed()  # Keeps the server running

if __name__ == "__main__":
    asyncio.run(main())