from pymongo import MongoClient
from dotenv import load_dotenv
import os



load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


client = MongoClient(MONGO_URI)
db = client["chatSportsDB"]
users = db["users"]
rooms = db["rooms"]



# INSERTING:
def insert_room(room):
    rooms.insert_one(room)
def add_user(user):
    users.insert_one(user)

# DELETING:
def delete_room(room):
    result = rooms.delete_one(room)
    if result.deleted_count > 0:
        return True
    else:
        return False
def delete_user(user):
    result = users.delete_one(user)
    if result.deleted_count > 0:
        return True
    else:
        return False
 
# SEARCHING:

def find_user_by_username(username):
    return users.find_one({"username": username})
#async def find_user_by_websocket(websocket):
  #  return users.find_one({"websocket": websocket})
# Function to check if a room exists by its name
def room_exists_by_name(room_name):
    return rooms.find_one({"name": room_name})


#GETTING:

# getting all users from a specific room
def get_users_in_room(room):
    if room:
        return room.get("users", [])
    return []
def get_num_of_rooms():
    return rooms.count_documents({})
def get_num_of_users():
    return users.count_documents({})

    

 #UPDATING:

 # Function to add a user to a room
def add_user_to_room(room, user):
    result = rooms.update_one(
        {"name": room["name"]},  # Filter to find the room by name
        {"$addToSet": {"users": user["id"]}}  # Add the user to the "users" array if not already present
    )
    return result.modified_count > 0  # Returns True if the user was added
def add_room_to_user(user, room):
    result = users.update_one(
        {"username": user["username"]},
        {"$addToSet": {"rooms": room["id"]}}
    )
    return result.modified_count > 0
# Function to remove a user from a room
def remove_user_from_room(room, user):
    result = rooms.update_one(
        {"name": room["name"]},  # Filter to find the room by name
        {"$pull": {"users": user["id"]}}
           )
    return result.modified_count > 0  # Returns True if the user was removed  # Remove the user from the "users" array

def remove_user_from_rooms(user):
    rooms_of_user = user.get("rooms", []) # get all the rooms the user belongs to right now
    for room in rooms_of_user:
        if room:
            room["users"].remove(user["id"])
            # update it inside the db:
            rooms.update_one( 
             {"name": room["name"]}, 
            {"$set": {"users": list(room["users"])}}
)
    users.update_one({"username": user["username"]}, {"$set": {"rooms": []}}) # why this line?

def remove_room_from_user(username,room):
    result = users.update_one(
    {"username": username},  # Filter to find the room by name
    {"$pull": {"rooms": room["id"]}}
        )
    return result.modified_count > 0  # Returns True if the user was removed  # Remove the user from the "users" array