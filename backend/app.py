from flask import Flask, jsonify
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Password Manager API!"

@app.route('/generate-password', methods=['GET'])
def get_password():
    password = generate_password()
    return jsonify({'password': password})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)