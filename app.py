from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['webhook_db']
collection = db['actions']

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json  # Get the JSON payload from GitHub webhook
    event_type = request.headers.get('X-GitHub-Event')  # Get the event type
    author = payload['sender']['login']  # Get the author of the action
    timestamp = datetime.utcnow()  # Set the current timestamp

    # Handle different types of events
    if event_type == 'push':
        to_branch = payload['ref'].split('/')[-1]  # Get the branch
        action_data = {
            'author': author,
            'to_branch': to_branch,
            'timestamp': timestamp,
            'action_type': 'push'
        }

    elif event_type == 'pull_request':
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        action_data = {
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp,
            'action_type': 'pull_request'
        }

    # Save the action to MongoDB
    collection.insert_one(action_data)
    
    return jsonify({'message': 'Action recorded'}), 200

if __name__ == '__main__':
    app.run(debug=True)

