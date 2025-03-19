import os
import secrets
from datetime import timedelta
import codecs
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from pymongo import MongoClient

load_dotenv()

# def init():
#     global users_collection, app
    # Set up the MongoDB client and database
app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem' # os.getenv('SESSION_TYPE', 'filesystem')  # Default to 'filesystem' if not set
app.config['SESSION_PERMANENT'] = True # os.getenv('SESSION_PERMANENT', 'True') == 'True'  # Convert string to boolean
app.config['SESSION_USE_SIGNER'] = True # os.getenv('SESSION_USE_SIGNER', 'True') == 'True'  # Convert string to boolean
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

Session(app)

CORS(app, supports_credentials=True)  # Allow CORS for all routes
client = MongoClient("mongodb://localhost:27017/")  # Change the URI if needed
db = client["health_database"]  # Database name
users_collection = db["users"]  # Collection name for users

active_sessions = {}

@app.route('/api/signup', methods=['POST'])
def create_user():
    # Hash the password before storing it in the database
    data = request.get_json()
    name, email, password, age, gender, height, weight, allergies, medical_history = data["name"], data["email"], data["password"], data["age"], data["gender"], data["height"], data["weight"], data["allergies"], data["medical_history"]
    hashed_password = codecs.encode(password.encode('utf-8'),'base64','strict')

    # Create a new user dictionary
    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "allergies": allergies,
        "medical_history": medical_history,
        "conversation_transcripts": [],
        "symptoms": []
    }

    # Insert the user into the MongoDB collection
    users_collection.insert_one(user_data)
    print(f"User {name} created successfully!")
    return jsonify({"message": "yeah added player"}), 200


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    session.permanent = True
    email, password = data["email"], data["password"]
    # Check if email or password are missing
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    # Find the user by email
    user = users_collection.find_one({"email": email})


    if user:
        # Check if the password matches the hashed password in the database
        #mistake might be there check
        if password.encode('utf-8') == codecs.decode(user['password'],'base64','strict'):
            print("Login successful!")
            id = secrets.token_urlsafe(32)
            active_sessions[id] = user['email']
            session['user_id'] = str(id)
            print(session['user_id'])
            print(session)
            return jsonify({"message": "Login successful!"}), 200
        else:
            print("Invalid password!")
            return jsonify({"message": "wrong psswd"}), 401
    else:
        print("User not found!")
        return jsonify({"message": "wrong psswd"}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.permanent = True
    # Clear session on logout
    session.pop('user_id', None)
    print("Logged out successfully!")
    return jsonify({"message": "Logged out successfully!"}), 200

@app.route('/api/isLoggedIn', methods=['POST'])
def is_logged_in():
    session.permanent = True
    # Clear session on logout
    print(session)
    if 'user_id' in session.keys():
        print(session['user_id'] + " is logged in.")
        return jsonify({"message": "yes, yes you are"}), 200
    return jsonify({"message": "no, you are not"}), 401

# @app.route('/api/doctorDashboard', methods=['POST'])
# def doctor():
#     for i in users_collection:
#         out = ;
#     ;
@app.route('/api/doctorDashboard', methods=['GET'])
def doctor():
    users = users_collection.find()  # Fetch all users from the database
    result = []

    # Iterate over each user in the collection
    for user in users:
        # Remove sensitive data (email and password)
        user_data = {
            "name": user["name"],
            "age": user["age"],
            "gender": user["gender"],
            "height": user["height"],
            "weight": user["weight"],
            "allergies": user["allergies"],
            "medical_history": user["medical_history"],
            "conversation_transcripts": user.get("conversation_transcripts", ""),
            "symptoms": user.get("symptoms", "")
        }
        result.append(user_data)
    
    # Return the filtered list of users
    return jsonify(result), 200

@app.route('/api/webAdminDashboard', methods=['POST'])
def webAdmin():
    data = request.get_json()
    users = users_collection.find()  # Fetch all users from the database
    result = []

    # Iterate over each user in the collection
    for user in users:
        # Remove sensitive data (email and password)
        user_data = {
            "email": user["email"],
            "password": codecs.decode(user["password"],'base64','strict'),
            "name": user["name"],
            "age": user["age"],
            "gender": user["gender"],
            "height": user["height"],
            "weight": user["weight"],
            "allergies": user["allergies"],
            "medical_history": user["medical_history"],
            "conversation_transcripts": user.get("conversation_transcripts", ""),
            "symptoms": user.get("symptoms", "")
        }
        result.append(user_data)
    
    # Return the filtered list of users
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, port=8080)


# if __name__ == '__main__':
#     name = "John Doe"
#     email = "sfd@sdf.sd"
#     password = "8pg7dPeHnBA63^a"
#     age = 30
#     gender = "Male"
#     height = 180  # in cm
#     weight = 75   # in kg
#     allergies = ["Peanuts", "Dust"]
#     medical_history = ["Asthma", "High blood pressure"]
#
#     create_user(name, email, password, age, gender, height, weight, allergies, medical_history)
#
#     login(email, password)

