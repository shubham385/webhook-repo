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
    # Get the JSON payload from GitHub webhook
    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')
    author = payload['sender']['login']
    timestamp = datetime.utcnow()

    # Handle different types of events
    if event_type == 'push':
        to_branch = payload['ref'].split('/')[-1]
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
    elif event_type == 'pull_request' and payload['action'] == 'closed' and payload['pull_request']['merged']:
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        action_data = {
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp,
            'action_type': 'merge'
        }

    # Save the action data to MongoDB
    collection.insert_one(action_data)

    return jsonify({'message': 'Action recorded'}), 200

if __name__ == '__main__':
    app.run(debug=True)

