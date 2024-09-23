# chatEs - Chat Only For Sports!

### About
Welcome to chatEs. the place where you can talk about any sports field you would like!
This python-written terminal-based project includes server-client communication, so you can talk about sports and sports only in a dedicated chat.
You can join whatever room you want, discuss about any topics and send private messages to anyone!

### What you can do
1. Join and create a room - join a room and get the last messages so you can follow the latest dicussion.
2. Private message
3. You will get notifications for each message you will get(pm or room message)
4. You can be a room admin or a room member - admin can add another member to be admin in a room, admin can remove a member in a room.
5. everything is stored in the database - user,room and messages collections. So nothing will get lost!

### Tech skills: 
- MongoDB
- Server-client communication using websockets
- Multi-threading using asyncio
- Jwt for authentication
- Notifications using winsound

### How to run:
1. ensure you have python installed on your computer
2. "python server.py"
3. "python client.py" - to every new client that want to connect to the chat 

### How to use: 
1. "join room_name" - user joins room_name
2. "leave room_name" - user leaves room_name
3. "pm user_name message_to_send" - user send a private message to user_name, while the message is message_to_send
4. "logout" - user logout from the chat
5. "remove user_name room_name" - admin user removes user_name from room_name (only if user == admin)
6. "add user_name room_name" - admin user add user_name to be admin in room_name (only if user == admin)
7. "room_name message_to_send" - user send a message(message_to_send) in room_name (only if user is in the room)


