import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        avatar TEXT DEFAULT 'avatar1.jpg'
    );
    ''')
    print("Users table created successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL
    );
    ''')
    print("Rooms table created successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        type TEXT DEFAULT 'text',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES rooms (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    ''')
    print("Messages table created successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS friends (
        user1_id INTEGER NOT NULL,
        user2_id INTEGER NOT NULL,
        PRIMARY KEY (user1_id, user2_id),
        FOREIGN KEY (user1_id) REFERENCES users (id),
        FOREIGN KEY (user2_id) REFERENCES users (id)
    );
    ''')
    print("Friends table created successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS friend_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER NOT NULL,
        to_user_id INTEGER NOT NULL,
        FOREIGN KEY (from_user_id) REFERENCES users (id),
        FOREIGN KEY (to_user_id) REFERENCES users (id)
    );
    ''')
    print("Friend requests table created successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS team_stats (
        team_code TEXT PRIMARY KEY,
        team_name TEXT NOT NULL,
        completion_percentage INTEGER NOT NULL DEFAULT 0 CHECK(completion_percentage >= 0 AND completion_percentage <= 100)
    );
    ''')
    print("Team stats table created successfully")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
