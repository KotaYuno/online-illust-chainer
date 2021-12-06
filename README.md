# Online Illust Chainer
#### Video Demo:  <https://youtu.be/xRcmajYSGPE>
#### Description:
## Features
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)

I've used Flask web framework based in Python.
And I've used Flask-SocketIO to communicate with server.

### Explaining the project
My final project is a web application that can play illust chainer that is called "絵しりとり" in Japanese.
Because of the pandemic of corona virus, online drinking party has increased.
So I decided to make a game that everyone can play there.

My web application has two pages.
- log-in page
- playroom page

#### log-in-page
There are two tabs.
- 作成(=make room)
- log-in

##### make-room
You can make a room here.
There are three items to enter.
- room name
- password
- player name

If you did not enter room name and password, an error will occur and you will be asked to enter it again.
items that is entered is saved in not datebase but memory as lists.
And when no one is out of the room, the list will be deleted.

##### log-in
You can log in a room here.
There are three items to enter.

- room name
- password
- player name

If you did not enter the three items, an error will occur and you will be asked to enter it again.
Player name is saved in list.
If If there is already a person with the same name in the room, you will be asked to enter it again.


#### playroom-page
You can play "Shiritori" here.
On the top of the page, The current room name and current writer are displayed.

- canvas
- players list
- some buttons
- log

##### canvas
You can draw a picture on the canvas.
This is implemented using js.
Synchronizes with other screens by sending the x and y coordinates of the cursor being dragged.
The buttons described below are similar, but they won't work until it's your turn.

##### players list
A list of the names of the players currently in the room.
The name will be deleted when player leave the room.

##### some buttons
there are four button.
- clear:
If you push this button, canvas will be clear.
- eraser:
If push this button, pan mode will change eraser.
- submit:
If push this button, picture will be send to server, and it will become the next person's turn.
If push this button without writing anything on the canvas, you will be asked to write something.
- leave:
If push this button, you leave this room.


#### log
Log is displayed here.
when no one is out of the room, the log of the room will be deleted.