import logging
import sqlite3
import os
import random
import string
from functools import wraps
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'passwords.db')

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

FERNET_KEY = os.getenv('SECRET_KEY').encode()
cipher = Fernet(FERNET_KEY)


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            site TEXT,
            username TEXT,
            password TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute("PRAGMA table_info(passwords)")
    password_table_columns = [row['name'] for row in cursor.fetchall()]
    if 'user_id' not in password_table_columns:
        cursor.execute('ALTER TABLE passwords ADD COLUMN user_id INTEGER')

    conn.commit()
    conn.close()


app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('APP_SECRET_KEY', 'change-me-in-production')


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get('user_id'):
            if request.path.startswith('/passwords'):
                return jsonify({'message': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return view(*args, **kwargs)

    return wrapped_view

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/', methods=['GET'])
def root():
    if session.get('user_id'):
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('user_id'):
            return redirect(url_for('index'))
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        return render_template('login.html', error='Username and password are required.')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return render_template('login.html', error='Invalid username or password.')

    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']

    return redirect(url_for('index'))

@app.route('/signup', methods=['GET'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not username or not password:
        return render_template('signup.html', error='Username and password are required.')

    if password != confirm_password:
        return render_template('signup.html', error='Passwords do not match.')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return render_template('signup.html', error='Username already exists.')

    conn.close()

    return render_template('login.html', success='Account created. Please log in.')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/manager', methods=['GET'])
@login_required
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/generate-password', methods=['GET'])
def get_password():
    password = generate_password()
    return jsonify({'password': password})

@app.route('/passwords', methods=['POST'])
@login_required
def add_password():
    data = request.get_json(silent=True) or {}
    site = data.get('site', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not site or not username or not password:
        return jsonify({'message': 'Site, username, and password are required.'}), 400

    encrypted_password = cipher.encrypt(password.encode())
    logging.debug(f"Encrypted password: {encrypted_password}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO passwords (user_id, site, username, password) VALUES (?, ?, ?, ?)',
        (session['user_id'], site, username, encrypted_password)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Password added successfully'})

@app.route('/passwords', methods=['GET'])
@login_required
def get_passwords():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, site, username, password FROM passwords WHERE user_id = ?', (session['user_id'],))
    passwords = cursor.fetchall()
    conn.close()

    result = []
    for password in passwords:
        result.append({
            'id': password['id'],
            'site': password['site'],
            'username': password['username'],
            'password': cipher.decrypt(password['password']).decode()
        })

    return result

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", debug=True)