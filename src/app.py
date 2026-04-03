import logging
import sqlite3
import os
import random
import string
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv
from cryptography.fernet import Fernet


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'passwords.db')

print(f"Base directory: {BASE_DIR}")

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

print(os.getenv('SECRET_KEY'))

FERNET_KEY = os.getenv('SECRET_KEY').encode()
cipher = Fernet(FERNET_KEY)

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT,
            username TEXT,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


app = Flask(__name__)
CORS(app)

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate-password', methods=['GET'])
def get_password():
    password = generate_password()
    return jsonify({'password': password})

@app.route('/passwords', methods=['POST'])
def add_password():
    data = request.json
    encrypted_password = cipher.encrypt(data.get('password').encode())
    logging.debug(f"Encrypted password: {encrypted_password}")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO passwords (site, username, password) VALUES (?, ?, ?)',
                   (data.get('site'), data.get('username'), encrypted_password))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Password added successfully'})

@app.route('/passwords', methods=['GET'])
def get_passwords():
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM passwords')
    passwords = cursor.fetchall()
    conn.close()

    result = []
    for password in passwords:
        result.append({
            'id': password[0],
            'site': password[1],
            'username': password[2],
            'password': cipher.decrypt(password[3]).decode()
        })

    return result

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", debug=True)