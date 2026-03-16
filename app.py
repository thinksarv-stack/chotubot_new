import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS so your Netlify frontend can talk to this Render backend
CORS(app)

# Pulls the API key from Render's Environment Variables
# If not found, it defaults to a placeholder (but you should set it in Render)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your_api_key_here")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route('/health', methods=['GET'])
def health():
    """Route to check if the server is awake"""
    return jsonify({"status": "online", "message": "Server is active"}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful voice assistant. Keep answers short, natural, and clear."
                },
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 200
        }

        response = requests.post(GROQ_URL, headers=headers, json=payload)
        
        # Check if Groq returned an error
        if response.status_code != 200:
            return jsonify({
                "error": "Groq API Error", 
                "details": response.text
            }), response.status_code

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render assigns a dynamic port, we must listen on 0.0.0.0
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)