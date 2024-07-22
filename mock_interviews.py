from flask import Flask, request, jsonify, render_template
import openai
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Set the OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint to chat with the OpenAI model.
    """
    user_message = request.json.get('message')
    logging.debug(f"User message: {user_message}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message['content'].strip()
        logging.debug(f"Bot reply: {reply}")
        return jsonify({'reply': reply})
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)















