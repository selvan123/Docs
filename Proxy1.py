@app.route('/proxy', methods=['POST'])
def proxy():
    try:
        # Try parsing JSON body
        data = request.get_json()
        print("Received payload:", data)

        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        # For testing: use a known good public POST endpoint
        target_url = "https://httpbin.org/post"

        # Forward request
        response = requests.post(target_url, json=data, headers={
            'Content-Type': 'application/json'
        })

        # Return the actual response content from the target
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as req_err:
        print("Request to target API failed:", req_err)
        return jsonify({"error": "Request to target API failed", "details": str(req_err)}), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500
