from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import random
import string

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'passwords.db')

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

#TODO: Implement encryption and decryption for stored passwords
#def encrypt(password):
#    # Placeholder for encryption logic
#    return password  # In a real application, implement proper encryption here
#
#def decrypt(encrypted_password):
#    # Placeholder for decryption logic
#    return decrypted_password  # In a real application, implement proper decryption here

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Password Manager API!"

@app.route('/generate-password', methods=['GET'])
def get_password():
    password = generate_password()
    return jsonify({'password': password})

@app.route('/passwords', methods=['POST'])
def add_password():
    data = request.json
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO passwords (site, username, password) VALUES (?, ?, ?)',
                   (data.get('site'), data.get('username'), data['password']))
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
            'password': password[3]
        })

    return result

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", debug=True)