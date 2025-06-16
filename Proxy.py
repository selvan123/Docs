from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Proxy endpoint
@app.route('/proxy', methods=['POST'])
def proxy():
    try:
        # Body received from GitHub, webhook, etc.
        incoming_data = request.get_json()
        print("Received data:", incoming_data)

        # Replace this with your actual target API (e.g., Azure DevOps)
        target_url = "https://jsonplaceholder.typicode.com/posts"

        # Forward the request
        headers = {
            'Content-Type': 'application/json',
            # 'Authorization': 'Bearer YOUR_TOKEN'  # Optional
        }

        response = requests.post(target_url, json=incoming_data, headers=headers)

        # Return target response back to original caller
        return jsonify(response.json()), response.status_code

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Something went wrong"}), 500

# Root route
@app.route('/')
def index():
    return 'Proxy API is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
