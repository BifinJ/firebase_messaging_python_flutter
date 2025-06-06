from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.messaging import UnregisteredError, BatchResponse # Add error handling imports

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# 🔑 Initialize Firebase Admin SDK
# Replace 'path/to/your/serviceAccountKey.json' with the actual path
# Make sure this file is secured and not exposed publicly!
cred = credentials.Certificate('path/to/your/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# 🔒 Temporary in-memory storage (replace with DB if needed)
user_tokens = {}  # Format: {user_id: token}
todos = []

# 🔌 Register a device token
@app.route('/register-device', methods=['POST'])
def register_device():
    print("Received request to register device") # Added print for debugging
    data = request.json
    user_id = data['user_id']
    token = data['token']
    user_tokens[user_id] = token
    print(f"Registered token for user {user_id}: {token}") # Added print for debugging
    return jsonify({"status": "Device registered"}), 200

# 📝 Schedule a task
@app.route('/create-task', methods=['POST'])
def create_task():
    data = request.json
    # Consider adding validation for required fields in 'data' and 'details'
    if data.get("type") != "create_task":
        return jsonify({"error": "Invalid task type"}), 400

    details = data.get("details")
    if not details:
        return jsonify({"error": "Missing details"}), 400

    name = details.get("name")
    date_str = details.get("date")
    time_str = details.get("time")
    user_id = data.get("user_id")

    if not all([name, date_str, time_str, user_id]):
         return jsonify({"error": "Missing required fields (name, date, time, user_id)"}), 400

    if user_id not in user_tokens:
        return jsonify({"error": "User device token not registered"}), 400

    try:
        reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        # Ensure the scheduled time is in the future
        if reminder_time <= datetime.now():
             return jsonify({"error": "Scheduled time must be in the future"}), 400

    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400

    # Schedule push using APScheduler
    scheduler.add_job(send_push, 'date', run_date=reminder_time, args=[user_tokens[user_id], name, user_id]) # Pass user_id for potential logging/error handling

    print(f"Task '{name}' scheduled for user {user_id} at {reminder_time}") # Added print
    todos.append({
        "name": name,
        "date": date_str,
        "time": time_str,
        "user_id": user_id,
        "completed": False  # 🆕 Add completed status
    })
    return jsonify({
        "status": "scheduled",
        "message": f"✅ Task \"{name}\" has been scheduled for {date_str} at {time_str}."
    }), 200

# 🔔 Function to send push notification using Firebase Admin SDK
def send_push(token, task_name, user_id): # Added user_id argument
    print(f"Attempting to send push to user {user_id} with token {token} for task '{task_name}'") # Added print

    # Construct the message payload using Admin SDK
    message = messaging.Message(
        notification=messaging.Notification(
            title='Reminder',
            body=task_name,
        ),
        token=token,
    )

    try:
        # Send the message
        response = messaging.send(message)
        print('Successfully sent message:', response) # response is the message ID

    except UnregisteredError:
        # This token is no longer valid, likely the app was uninstalled or token refreshed
        print(f'App instance has been unregistered for user {user_id}. Removing token: {token}')
        # You should remove this token from your database (user_tokens in this simple example)
        if user_id in user_tokens and user_tokens[user_id] == token:
             del user_tokens[user_id]
             print(f"Removed token for user {user_id}")

    except Exception as e: # Catch other potential errors
        print(f'Failed to send notification to user {user_id} with token {token}: {e}')
        # Implement retry logic or logging for other errors (like UnavailableError)

# 📥 Get all scheduled todos
@app.route('/get-todos', methods=['GET'])
def get_todos():
    return jsonify({
        "status": "success",
        "todos": todos
    }), 200

# 🔄 Toggle completion status of a task
@app.route('/toggle-task-status', methods=['POST'])
def toggle_task_status():
    data = request.json
    user_id = data.get("user_id")
    name = data.get("name")

    if user_id is None or name is None:
        return jsonify({"error": "Missing user_id or name field"}), 400

    toggled = False
    for task in todos:
        if task["user_id"] == user_id and task["name"] == name:
            task["completed"] = not task["completed"]  # ✅ Toggle the boolean
            toggled = True
            break

    if toggled:
        return jsonify({
            "status": "success",
            "message": f"Task '{name}' marked as {'completed' if task['completed'] else 'incomplete'}."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": f"Task '{name}' not found for user '{user_id}'."
        }), 404

    
if __name__ == '__main__':
    # In a production environment, you wouldn't run with debug=True
    # and you would deploy this server (e.g., to Cloud Run, App Engine, etc.)
    print("Server is running on port 5000") # Added print for server start confirmation
    app.run(debug=True, port=5000) # Specify a port

