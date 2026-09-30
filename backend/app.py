from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash


# ================= PATHS =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
DATABASE_PATH = os.path.join(BASE_DIR, "chat.db")


# ================= FLASK =================

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)


# ================= DATABASE =================

connection = sqlite3.connect(DATABASE_PATH)

print(
    "DATABASE USED:",
    connection.execute(
        "PRAGMA database_list"
    ).fetchone()
)

cursor = connection.cursor()


# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")


# Messages table
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    message TEXT
)
""")


connection.commit()
connection.close()


# ================= HOME =================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# ================= FRONTEND =================

@app.route("/<path:filename>")
def frontend(filename):

    return send_from_directory(
        FRONTEND_DIR,
        filename
    )


# ================= REGISTER =================

@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]


    if password != confirm_password:

        return """
        <h1>Registration Failed</h1>

        <p>Passwords do not match.</p>

        <a href="/register.html">
        Go Back
        </a>
        """


    # Password hashing
    hashed_password = generate_password_hash(password)


    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()


    try:

        cursor.execute(
            """
            INSERT INTO users
            (username, email, password)
            VALUES (?, ?, ?)
            """,
            (
                username,
                email,
                hashed_password
            )
        )

        connection.commit()


    except sqlite3.IntegrityError:

        connection.close()

        return """
        <h1>Registration Failed</h1>

        <p>
        Username or email already exists.
        </p>

        <a href="/register.html">
        Go Back
        </a>
        """


    connection.close()


    return """
    <h1>Registration Successful!</h1>

    <p>
    Your account has been created securely.
    </p>

    <a href="/login.html">
    Go to Login
    </a>
    """


# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]


    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()


    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )


    user = cursor.fetchone()

    connection.close()


    if user and check_password_hash(
        user[3],
        password
    ):

        return f"""
        <script>

            localStorage.setItem(
                "username",
                "{user[1]}"
            );

            window.location.href =
                "/chat.html";

        </script>
        """


    return """
    <h1>Login Failed</h1>

    <p>
    Invalid username or password.
    </p>

    <a href="/login.html">
    Try Again
    </a>
    """


# ================= SOCKET CONNECT =================

@socketio.on("connect")
def handle_connect():

    print(
        "User connected to chat"
    )


# ================= SOCKET MESSAGE =================

@socketio.on("message")
def handle_message(data):

    print(
        "Message received:",
        data
    )


    username = data["username"]
    message = data["message"]


    # Save message in database

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO messages
        (username, message)
        VALUES (?, ?)
        """,
        (
            username,
            message
        )
    )


    connection.commit()
    connection.close()


    # Send message to all connected users

    socketio.emit(
        "message",
        {
            "username": username,
            "message": message
        }
    )


# ================= SOCKET DISCONNECT =================

@socketio.on("disconnect")
def handle_disconnect():

    print(
        "User disconnected from chat"
    )


# ================= START SERVER =================

if __name__ == "__main__":

    print(
        "Flask Socket Server Started"
    )


    port = int(
        os.environ.get(
            "PORT",
            8000
        )
    )


    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )