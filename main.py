from flask import Flask, render_template, request, redirect, session, url_for, g, flash
from flask_socketio import SocketIO, join_room, leave_room, send
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from werkzeug.utils import secure_filename
import base64
import uuid
import datetime
import functools
from database import init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "R09maW5nQG9uZQ==")
app.config["DATABASE"] = "database.db"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['AVATAR_FOLDER'] = 'static/avatars'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize database on app startup
@app.before_request
def before_request_func():
    try:
        if not hasattr(app, 'db_initialized'):
            init_db()
            app.db_initialized = True
    except Exception as e:
        print(f"Database initialization error: {e}")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

def generate_room_code(length=4):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

def sync_team_stats(db):
    """Synchronize rooms data to team_stats table"""
    try:
        # Insert new public rooms (non-private) into team_stats if not present
        db.execute('''
            INSERT OR IGNORE INTO team_stats (team_code, team_name, completion_percentage)
            SELECT code, name, 0
            FROM rooms
            WHERE code NOT LIKE 'private_%'
        ''')
        
        # Update team names to match current room names
        db.execute('''
            UPDATE team_stats
            SET team_name = (
                SELECT r.name
                FROM rooms r
                WHERE r.code = team_stats.team_code
                LIMIT 1
            )
            WHERE team_code IN (
                SELECT code FROM rooms WHERE code NOT LIKE 'private_%'
            )
        ''')
        
        db.commit()
    except Exception as e:
        print(f"Error in sync_team_stats: {e}")
        db.rollback()

        db.rollback()

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("login"))
        
        flash(error)
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))

        flash(error)

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    sync_team_stats(db)

    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    rooms = db.execute('SELECT * FROM rooms').fetchall()
    team_stats = db.execute(
        'SELECT team_name, completion_percentage FROM team_stats ORDER BY completion_percentage DESC, team_name ASC'
    ).fetchall()
    
    friend_requests = db.execute(
        'SELECT fr.id, u.username FROM friend_requests fr JOIN users u ON fr.from_user_id = u.id WHERE fr.to_user_id = ?',
        (session['user_id'],)
    ).fetchall()

    friends = db.execute(
        'SELECT u.id, u.username FROM friends f JOIN users u ON f.user2_id = u.id WHERE f.user1_id = ?',
        (session['user_id'],)
    ).fetchall()

    # Get list of available avatars
    available_avatars = [f for f in os.listdir(app.config['AVATAR_FOLDER']) if os.path.isfile(os.path.join(app.config['AVATAR_FOLDER'], f))]

    return render_template(
        'dashboard.html',
        user=user,
        rooms=rooms,
        friend_requests=friend_requests,
        friends=friends,
        available_avatars=available_avatars,
        team_stats=team_stats
    )

@app.route('/select_avatar', methods=['POST'])
@login_required
def select_avatar():
    avatar_filename = request.form['avatar_selection']
    
    db = get_db()
    db.execute(
        'UPDATE users SET avatar = ? WHERE id = ?',
        (avatar_filename, session['user_id'])
    )
    db.commit()
    
    flash('Avatar updated successfully.')
    return redirect(url_for('dashboard'))

@app.route('/chat/<int:friend_id>')
@login_required
def chat(friend_id):
    db = get_db()
    
    user_id = session['user_id']
    if user_id < friend_id:
        room_code = f'private_{user_id}_{friend_id}'
    else:
        room_code = f'private_{friend_id}_{user_id}'

    room = db.execute('SELECT * FROM rooms WHERE code = ?', (room_code,)).fetchone()

    if room is None:
        friend = db.execute('SELECT * FROM users WHERE id = ?', (friend_id,)).fetchone()
        room_name = f"Chat with {friend['username']}"
        db.execute(
            'INSERT INTO rooms (name, code) VALUES (?, ?)',
            (room_name, room_code)
        )
        db.commit()

    return redirect(url_for('room', room_code=room_code))


@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    friend_username = request.form['username']
    if not friend_username:
        flash('Username is required.')
        return redirect(url_for('dashboard'))

    db = get_db()
    friend = db.execute(
        'SELECT * FROM users WHERE username = ?', (friend_username,)
    ).fetchone()

    if friend is None:
        flash('User not found.')
        return redirect(url_for('dashboard'))

    db.execute(
        'INSERT INTO friend_requests (from_user_id, to_user_id) VALUES (?, ?)',
        (session['user_id'], friend['id'])
    )
    db.commit()
    flash(f'Friend request sent to {friend_username}.')
    return redirect(url_for('dashboard'))

@app.route('/accept_friend/<int:request_id>')
@login_required
def accept_friend(request_id):
    db = get_db()
    request = db.execute(
        'SELECT * FROM friend_requests WHERE id = ? AND to_user_id = ?',
        (request_id, session['user_id'])
    ).fetchone()

    if request is None:
        flash('Invalid friend request.')
        return redirect(url_for('dashboard'))

    db.execute(
        'INSERT INTO friends (user1_id, user2_id) VALUES (?, ?)',
        (request['from_user_id'], request['to_user_id'])
    )
    db.execute(
        'INSERT INTO friends (user1_id, user2_id) VALUES (?, ?)',
        (request['to_user_id'], request['from_user_id'])
    )
    db.execute('DELETE FROM friend_requests WHERE id = ?', (request_id,))
    db.commit()
    
    flash('Friend request accepted.')
    return redirect(url_for('dashboard'))

@app.route('/decline_friend/<int:request_id>')
@login_required
def decline_friend(request_id):
    db = get_db()
    db.execute('DELETE FROM friend_requests WHERE id = ? AND to_user_id = ?', (request_id, session['user_id']))
    db.commit()

    flash('Friend request declined.')
    return redirect(url_for('dashboard'))

@app.route('/create_room', methods=['POST'])
@login_required
def create_room():
    room_name = request.form['room_name']
    if not room_name:
        flash('Room name is required.')
        return redirect(url_for('dashboard'))

    db = get_db()
    room_code = generate_room_code()
    db.execute(
        'INSERT INTO rooms (name, code) VALUES (?, ?)',
        (room_name, room_code)
    )
    db.commit()
    
    return redirect(url_for('room', room_code=room_code))

@app.route('/join_room', methods=['POST'])
@login_required
def join_room_route():
    room_code = request.form['room_code']
    if not room_code:
        flash('Room code is required.')
        return redirect(url_for('dashboard'))

    db = get_db()
    room = db.execute(
        'SELECT * FROM rooms WHERE code = ?', (room_code,)
    ).fetchone()

    if room is None:
        flash('Room not found.')
        return redirect(url_for('dashboard'))

    return redirect(url_for('room', room_code=room_code))


@app.route('/room/<room_code>')
@login_required
def room(room_code):
    db = get_db()
    room = db.execute(
        'SELECT * FROM rooms WHERE code = ?', (room_code,)
    ).fetchone()

    if room is None:
        flash('Room not found.')
        return redirect(url_for('dashboard'))

    messages = db.execute(
        'SELECT u.username, u.avatar, m.content, m.type FROM messages m JOIN users u ON m.user_id = u.id WHERE m.room_id = ? ORDER BY m.timestamp ASC',
        (room['id'],)
    ).fetchall()

    return render_template('room.html', room=room, messages=messages)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@socketio.on('join')
def on_join(data):
    username = session['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = session['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)

@socketio.on('message')
def handle_message(data):
    room_code = data['room']
    db = get_db()
    room = db.execute('SELECT * FROM rooms WHERE code = ?', (room_code,)).fetchone()

    if room:
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        db.execute(
            'INSERT INTO messages (room_id, user_id, content, type, timestamp) VALUES (?, ?, ?, ?, ?)',
            (room['id'], session['user_id'], data['msg'], 'text', datetime.datetime.now())
        )
        db.commit()
        send({'msg': data['msg'], 'user': user['username'], 'avatar': user['avatar'], 'type': 'text'}, to=room_code)

@socketio.on('audio')
def handle_audio(data):
    room_code = data['room']
    db = get_db()
    room = db.execute('SELECT * FROM rooms WHERE code = ?', (room_code,)).fetchone()

    if room:
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        audio_data = base64.b64decode(data['data'].split(",")[1])
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, "wb") as f:
            f.write(audio_data)
        
        url = f"/static/uploads/{filename}"
        
        db.execute(
            'INSERT INTO messages (room_id, user_id, content, type, timestamp) VALUES (?, ?, ?, ?, ?)',
            (room['id'], session['user_id'], url, 'audio', datetime.datetime.now())
        )
        db.commit()
        send({'msg': url, 'user': user['username'], 'avatar': user['avatar'], 'type': 'audio'}, to=room_code)

@socketio.on('pdf')
def handle_pdf(data):
    room_code = data['room']
    db = get_db()
    room = db.execute('SELECT * FROM rooms WHERE code = ?', (room_code,)).fetchone()

    if room:
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        pdf_data = base64.b64decode(data['data'].split(",")[1])
        filename = f"{uuid.uuid4()}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, "wb") as f:
            f.write(pdf_data)
        
        url = f"/static/uploads/{filename}"
        
        db.execute(
            'INSERT INTO messages (room_id, user_id, content, type, timestamp) VALUES (?, ?, ?, ?, ?)',
            (room['id'], session['user_id'], url, 'pdf', datetime.datetime.now())
        )
        db.commit()
        send({'msg': url, 'user': user['username'], 'avatar': user['avatar'], 'type': 'pdf'}, to=room_code)

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    send(data, to=data['room'], skip_sid=request.sid)

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    send(data, to=data['room'], skip_sid=request.sid)

@socketio.on('webrtc_ice_candidate')
def handle_webrtc_ice_candidate(data):
    send(data, to=data['room'], skip_sid=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)