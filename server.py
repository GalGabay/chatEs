import asyncio
import websockets
import jwt
from db import find_user_by_username, insert_room, delete_room, add_user,delete_user, room_exists_by_name, add_user_to_room, remove_user_from_room, get_users_in_room, remove_user_from_rooms, add_room_to_user,get_num_of_rooms

# move it to environemnt later:
SECRET_KEY = "my_secret_key"

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
user_connections = {} # not sure if i need this

async def connection(websocket):
    if not await authenticate(websocket):
        return  # Close the connection if authentication fails
    
    #users.add(websocket) # add the new client to the list of connected users

    # add the user to the room he asked for
    room_name = await websocket.recv()
    room = room_exists_by_name(room_name) # checks if there is a room with this name
    if not room:
        room_count = get_num_of_rooms()
        room = {
        "name": room_name,
        "id": room_count + 1,
        "users": []
        }
        insert_room(room)

    user_name = user_connections[websocket]
    user = find_user_by_username(user_name)
    add_user_to_room(user)
    add_room_to_user(user,room)
    #if room not in rooms["name"]:
    #    rooms[room] = set()
   # rooms[room].add(websocket)

    try:
        async for message in websocket:
            print(f"Server received: {message}")


            # Broadcast the received message to all connected users
            await asyncio.gather(*(user.send(message) for user in get_users_in_room(room))) # why gather and not wait?
           # await websocket.send(f"Received your message: {message}")
    except websockets.ConnectionClosedOK:
        print("Connection closed")
    finally:
        delete_user(user)
        remove_user_from_rooms(user) # ?? i want to remove the user from all rooms
        if get_users_in_room(room) == []:
            delete_room(room)
        #rooms[room].remove(websocket)
       # if not rooms[room]:
        #    del rooms[room]

async def authenticate(websocket):
    try:
        # Receive the authentication data (username and password)
        username = await websocket.recv()
        password = await websocket.recv()
        
        #user = await find_user_by_username(username)

        # Check username and password
        #if user and user["password"] == password:

            # creating the user using the user schema
        user_connections[websocket] = username
        user_to_add = {
            "username": username,
            "password": password,
            "rooms:": []
        }
        await add_user(user_to_add)
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