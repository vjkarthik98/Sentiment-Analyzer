from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import pipeline
import logging
import os

# Initialize the Flask application
# AWS EB looks for an 'application' variable
application = Flask(__name__, static_folder='static')
CORS(application)  # Allow cross-origin requests

# Set up logging
logging.basicConfig(level=logging.INFO)

# --- Model Loading ---
# Load the model only ONCE when the app starts
# This is critical for performance
try:
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    application.logger.info("Model loaded successfully.")
except Exception as e:
    application.logger.error(f"Error loading model: {e}")
    classifier = None

# --- Error Handlers ---
# These functions will return clean JSON errors

@application.errorhandler(400)
def bad_request(error):
    application.logger.warning(f"Bad Request: {error}")
    return jsonify({"error": "Bad Request", "message": str(error)}), 400

@application.errorhandler(500)
def internal_server_error(error):
    application.logger.error(f"Internal Server Error: {error}")
    return jsonify({"error": "Internal Server Error", "message": "The server encountered an unexpected condition."}), 500

# --- API Endpoint ---
@application.route("/analyze", methods=["POST"])
def analyze_sentiment():
    application.logger.info("Received a request to /analyze")
    
    # 1. Check if model is loaded
    if classifier is None:
        return internal_server_error("Model is not loaded.")

    # 2. Get and validate input data
    json_data = request.get_json()
    if not json_data or "text" not in json_data:
        # Using 400 Bad Request error handler
        from werkzeug.exceptions import BadRequest
        raise BadRequest("No 'text' field provided in JSON body.")

    text = json_data["text"]
    if not isinstance(text, str) or not text.strip():
        from werkzeug.exceptions import BadRequest
        raise BadRequest("'text' field must be a non-empty string.")
        
    # 3. Perform AI Inference (with error handling)
    try:
        # Truncate long inputs to 512 tokens, which is the model's max
        result = classifier(text, truncation=True)
        # result is a list: [{'label': 'POSITIVE', 'score': 0.99}]
        # We return just the first element
        return jsonify(result[0])
    
    except Exception as e:
        application.logger.error(f"Error during classification: {e}")
        return internal_server_error("Error processing text.")

# --- Frontend Serving ---
@application.route("/")
def health_check():
    # This is the default route. 
    # It can serve the app or a health check. Serving the app is more user-friendly.
    return send_from_directory(application.static_folder, 'index.html')

@application.route("/app")
def serve_app():
    # This serves the index.html file
    return application.send_static_file("index.html")

@application.route("/static/<path:path>")
def send_static(path):
    # This serves the .css and .js files
    return application.send_static_file(path)

# --- Main execution ---
# This is for running locally
if __name__ == "__main__":
    # Note: Using port 8080 as AWS EB sometimes prefers it, but 5000 is fine too.
    application.run(debug=True, host='0.0.0.0', port=5000)