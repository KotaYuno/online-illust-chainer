
import datetime
import base64
import cv2
import os
from flask.json import jsonify

import numpy as np
from flask import Flask, request, render_template, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect, emit
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps


async_mode = None
app = Flask(__name__)
app.config.from_object(__name__)

# #自動でテンプレートが読み取られるかの確認
# app.config["TEMPLATES_AUTO_RELOAD"] = True

# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# # socketio.run(app, debug=True)
# socketio.run(app, debug=True)

#key:room名, 値:パスワード
roomes = {}
#key:room名, 値:playerのリスト
user_in_room = {}
#key:player名, 値:sid
user_sid = {}
#key:room名, 値:現在のwriter
now_writer = {}
#true:消しゴムモード、false:ペンモード
now_isPen = {}
#key:room名,値:画像名のリスト
pictures = {}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("room") is None:
            return redirect("/")
        elif not session["room"] in roomes:
            return redirect("/")
        elif not session["player"] in user_in_room[session["room"]]:
            return redirect("/re")
        elif session["pass"] != roomes[session["room"]]:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def message_output(msg):
    session["message"] = msg


def exist_room(tmp):
    for name in roomes.keys():
        if tmp == name:
            return False
    return True

def exist_name(room, user):
    for name in user_in_room[room]:
        if user == name:
            return False
    return True

@app.route("/")
def index():
    message = session.get("message")
    if message is None:
        return render_template("index.html")
    return render_template("index.html", message=message)

@app.route("/playroom")
@login_required
def playroom():
    room = session["room"]
    return render_template("playroom.html",room_name=room, players=user_in_room[room], now_writer=now_writer[room])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")

    room_name = request.form.get("room_name")
    if not room_name:
        message_output("room名を入力してください")
        return redirect("/")
    
    room_pass = request.form.get('password')
    if not room_pass:
        message_output("パスワードを入力してください")
        return redirect("/")
    if exist_room(room_name):
        message_output("room名が存在しないか、パスワードが違います。正しいroom名とパスワードを入力してください")
        return redirect("/")
    if room_pass != roomes[room_name]:
        message_output("room名が存在しないか、パスワードが違います。正しいroom名とパスワードを入力してください")
        return redirect("/")
    

    user_name = request.form.get('player_name')
    if not user_name:
        message_output("名前を入力してください")
        return redirect("/")
    elif exist_name(room_name, user_name) == False:
        message_output("既に使われているuser名です。違う名前を入力してください。")
        return redirect("/")
    
    session.clear()
    session["room"] = room_name
    session["pass"] = room_pass
    session["player"] = user_name

    user_in_room[room_name].append(user_name)

    return redirect("/playroom")

@app.route("/make", methods=['GET', 'POST'])
def make_room():
    if request.method == 'GET':
        return redirect("/")
    
    room_name = request.form.get("room_name")
    if not room_name:
        message_output("room名を入力してください")
        return redirect("/")

    room_pass = request.form.get("password")
    if not room_pass:
        message_output("パスワードを入力してください")
        return redirect("/")

    for name in roomes.keys():
        if name == room_name:
            message_output("既に存在するroom名です。違う名前を入力してください")
            return redirect("/")
    
    user_name = request.form.get('player_name')
    if not user_name:
        user_name = "host"
    
    roomes[room_name] = room_pass
    user_in_room[room_name] = list()
    user_in_room[room_name].append(user_name)
    now_writer[room_name] = user_name
    now_isPen[room_name] = False

    pictures[room_name] = list()

    session.clear()
    session["room"] = room_name
    session["pass"] = room_pass
    session["player"] = user_name
    return redirect("/playroom")

@app.route("/re")
def re():
    room = session["room"]
    player = session["player"]
    user_in_room[room].append(player)
    return redirect("/playroom")

@app.route("/pic", methods=["POST"])
def recive_pic():
    date = request.get_json()
    # #fetchで送られてきたstrの変換された画像データ
    # literal_date = date['date']
    # #バイナリデータに変換
    # binary_pic = literal_date.replace('data:image/png;base64,', '')
    # #デコード
    # array_pic = base64.b64decode(binary_pic)
    # #多次元配列を解消
    # png = np.frombuffer(array_pic, dtype=np.uint8)
    # img = cv2.imdecode(png, cv2.IMREAD_COLOR)
    # #ファイル名の作成,ファイル名：user名 + "_" + 日時
    # username = session["player"]
    # now_time = datetime.datetime.now()
    # now_time_str = str(now_time).replace(' ', "").replace(".", "_").replace("-", "_").replace(":", "_")
    # filename = str(username) + "_" +now_time_str + ".png"
    # #画像を保存
    # cv2.imwrite(os.path.join("static/pic", filename), img)

    room = session["room"]
    # pictures[room].append(filename)

    # socketio.emit('server_pic', {"file_name":filename, "user_name":username}, to=room)
    resuponsu = {'result': True}
    socketio.emit('server_clear_button', to=room)
    return jsonify(resuponsu)


def send_writer():
    room = session["room"]
    if not room in user_in_room:
        return True
    room_users = user_in_room[room]
    if len(room_users) == 1:
        return True
    now_user = room_users.index(session["player"])
    if len(room_users) - 1 == now_user:
        next_user_name = room_users[0]
    else:
        next_user_name = room_users[now_user + 1]
    next_user_sid = user_sid[next_user_name]
    now_writer[room] = next_user_name
    emit('select_writer', to=next_user_sid)
    emit('who_writer', next_user_name, to=room)
    return False

def close(room):
    #部屋情報の削除
    del user_in_room[room]
    del roomes[room]
    for filename in pictures[room]:
        os.remove("static/pic/" + filename)
    del pictures[room]
    
@socketio.on('join')
def on_join():
    username = session["player"]
    room = session["room"]
    join_room(room)
    user_sid[username] = request.sid
    if user_in_room[room][0] == username:
        emit('select_writer', to=user_sid[username])
    emit('after_join',username, to=room)
    if now_isPen[room]:
        emit('server_eraser', to=user_sid[username])
    if room in pictures.keys():
        for picture in pictures[room]:
            user = picture.split('_')[0]
            emit('server_pic',{"file_name":picture, "user_name":user}, to=user_sid[username])
    

# @socketio.on('leave')
# def on_leave():
#     username = session["player"]
#     room = session["room"]
#     emit('after_leave',username, to=room)
#     if send_writer() == 1:
#         leave_room(room)
#         close_room(room)
#         close(room)
#     else:
#         leave_room(room)
#         user_in_room[room].remove(username)
#     session.clear()

@socketio.on('client_to_server')
def draw(json):
    room=session["room"]
    emit('server_to_client', {'x':json['x'], 'y':json['y']}, to=room)

@socketio.on('clear_button')
def clear_canvas():
    room = session["room"]
    emit('server_clear_button', to=room)

@socketio.on('drag_end_client')
def drag_start():
    room = session["room"]
    emit('drag_end_server', to=room)

@socketio.on('drag_start_client')
def drag_start():
    room = session["room"]
    emit('drag_start_server', to=room)

@socketio.on('eraser_button')
def eraser_button():
    room = session["room"]
    if now_isPen[room]:
        now_isPen[room] = False
    else:
        now_isPen[room] = True
    emit('server_eraser', to=room)

@socketio.on('end_button')
def trun_end():
    send_writer()

@socketio.on('disconnect')
def disconnect():
    room = session["room"]
    player = session["player"]
    print("disconnect")
    if send_writer():
        close_room(room)
        close(room)
    else:
        emit('after_leave',player, to=room)
        user_in_room[room].remove(player)
    session.clear()

    
if __name__ == "__main__":
    app.run()