from pymongo import MongoClient

# move it to environemnt later:
MONGO_URI = "mongodb+srv://galgabay1999:bony5250@chatappcluster.jco5v.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["chatSportsDB"]
users = db["users"]
rooms = db["rooms"]



# INSERTING:
def insert_room(room):
    rooms.insert_one(room)
async def add_user(user):
    users.insert_one(user)

# DELETING:
async def delete_room(room):
    result = rooms.delete_one(room)
    if result.deleted_count > 0:
        return True
    else:
        return False
async def delete_user(user):
    result = users.delete_one(user)
    if result.deleted_count > 0:
        return True
    else:
        return False
 
# SEARCHING:

async def find_user_by_username(username):
    return users.find_one({"username": username})
#async def find_user_by_websocket(websocket):
  #  return users.find_one({"websocket": websocket})
# Function to check if a room exists by its name
async def room_exists_by_name(room_name):
    return rooms.find_one({"name": room_name})


#GETTING:

# getting all users from a specific room
def get_users_in_room(room):
    if room:
        return room.get("users", [])
    return []
def get_num_of_rooms():
    return rooms.count_documents({})

    

 #UPDATING:

 # Function to add a user to a room
def add_user_to_room(room, user):
    result = rooms.update_one(
        {"name": room},  # Filter to find the room by name
        {"$addToSet": {"users": user}}  # Add the user to the "users" array if not already present
    )
    return result.modified_count > 0  # Returns True if the user was added
def add_room_to_user(user, room):
    result = users.update_one(
        {"username": user},
        {"$addToSet": {"rooms": room}}
    )
    return result.modified_count > 0
# Function to remove a user from a room
def remove_user_from_room(room, user):
    result = rooms.update_one(
        {"name": room},  # Filter to find the room by name
        {"$pull": {"users": user}}
           )
    return result.modified_count > 0  # Returns True if the user was removed  # Remove the user from the "users" array

def remove_user_from_rooms(user):
    rooms_of_user = user.get("rooms", []) # get all the rooms the user belongs to right now
    for room in rooms_of_user:
        if room:
            room["users"].remove(user)
            # update it inside the db:
            rooms.update_one( 
             {"name": room["name"]}, 
            {"$set": {"users": list(room["users"])}}
)
    users.update_one({"username": user["name"]}, {"$set": {"rooms": []}}) # why this line?