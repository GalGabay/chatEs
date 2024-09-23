# chatEs - Chat Only For Sports!

### About
Welcome to chatEs, the place where you can talk about any sports field you like!
This python based terminal project features server-client communication, allowing you to have a sports-only discussions in dedicated chat rooms.
You can join any room, discuss various topics and send private messages to other users!

### Features
1. Join and create rooms - Enter any room and instantly catch up on the latest messages to follow the discussion.
2. Private messaging
3. Real-time notifications: Receive notifications for both private messages and room messages.
4. Role-based access: Become a room admin or a member. Admins can promote others to admin or remove members from a room.
5. Everything is stored in the database: All users, rooms, and messages are stored in a database, so nothing is ever lost!

### Tech Stack: 
- MongoDB: Database for storing users, rooms, and messages.
- WebSockets: Enables real-time server-client communication.
- Asyncio: For handling multi-threading.
- JWT: Used for secure authentication.
- Winsound: Provides notification sounds on message receipt.

### How to run:
1. Ensure you have python installed on your computer
2. Run the server: "python server.py"
3. For every new client, run: "python client.py"

### How to use - Useful commands: 
1. "join <room_name>" - Join a room called <room_name>.
2. "leave <room_name>" - Leave the room.
3. "pm <user_name> <message_to_send>" - Send a private message to <user_name>.
4. "logout" - Logout from the chat.
5. "remove <user_name> <room_name>" - As an admin, remove <user_name> from the room.
6. "add <user_name> <room_name>" - As an admin, promote <user_name> to admin the room.
7. "<room_name> <message_to_send>" - Send a message in the room you are part of.


