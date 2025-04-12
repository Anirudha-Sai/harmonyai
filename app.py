from flask import Flask, request, jsonify, send_file, render_template
import base64
import numpy as np
import soundfile as sf
import google.generativeai as genai
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__, static_folder='frontend', template_folder='frontend')
CORS(app, resources={r"/*": {"origins": "*"}})

colab_ngrok_url = None  # Global variable to store the Colab ngrok URL
my_api_key='AIzaSyC-87nB3pF8DFG0ZWCqdZ6he0Mm4TSNRqk'
# Configure the Gemini API
genai.configure(api_key=my_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/generate-gemini-prompt', methods=['POST'])
def generate_gemini_prompt():
    try:
        data = request.json
        current_mood = data.get('currentMood')
        instrument = data.get('instrument', 'any')
        duration = data.get('duration')
        
        # Create prompt for Gemini
        gemini_prompt = f"""Create a detailed prompt for a therapeutic music composition based on the following parameters:
        - Detected emotional state: {current_mood}
        - Main instrument focus: {instrument}
        - Desired duration: {duration} seconds

        The generated prompt should describe a soothing, emotionally supportive musical piece that aligns with and gently responds to the detected emotion. The {instrument} should be the main focus, carrying the melody or central texture, while other elements remain subtle and complementary. Include specific details about tempo (e.g., slow, moderate), mood (e.g., calming, uplifting), tonal quality (e.g., warm, mellow), and atmospheric setting (e.g., ambient background, natural sounds). The final prompt should guide the generation of music that promotes relaxation, emotional healing, and well-being.

        Return only the prompt text without any additional explanations or formatting."""

        
        # Generate content with Gemini
        response = model.generate_content(gemini_prompt)
        musicgen_prompt = response.text
        
        return jsonify({"prompt": musicgen_prompt})
    except Exception as e:
        print(f"Error generating prompt with Gemini: {str(e)}")
        return jsonify({"error": "Failed to generate prompt"}), 500

@app.route('/')
def serve_frontend():
    return render_template('index.html')

@app.route('/models/<path:path>')
def serve_models(path):
    models_dir = os.path.join(app.static_folder, 'models')
    return send_file(os.path.join(models_dir, path))

@app.route('/update_colab_ngrok_url', methods=['POST'])
@cross_origin()
def update_colab_ngrok_url():
    global colab_ngrok_url
    data = request.json
    colab_ngrok_url = data.get("colabNgrokUrl")
    if not colab_ngrok_url:
        return jsonify({"error": "Colab ngrok URL is missing."}), 400
    return jsonify({"message": "Colab ngrok URL updated successfully."}), 200

@app.route('/get_colab_ngrok_url', methods=['GET'])
@cross_origin()
def get_colab_ngrok_url():
    if colab_ngrok_url:
        return jsonify({"colabNgrokUrl": colab_ngrok_url}), 200
    else:
        return jsonify({"error": "Colab ngrok URL not set yet."}), 404

@app.route('/upload_audio', methods=['POST'])
@cross_origin()
def upload_audio():
    data = request.json
    audio_base64 = data.get('audio')
    sample_rate = data.get('sample_rate')

    if not audio_base64 or not sample_rate:
        return jsonify({"error": "Audio data or sample rate is missing."}), 400
    try:
        # Decode Base64 string to bytes
        audio_bytes = base64.b64decode(audio_base64)

        # Convert bytes to NumPy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.float32)

        # Save the audio to a file
        os.makedirs('static', exist_ok=True)
        sf.write('static/audio.wav', audio_array, int(sample_rate), subtype='PCM_16')
        return jsonify({"message": "Audio received and saved."}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to save audio: {str(e)}"}), 500

@app.route('/audio.wav', methods=['GET'])
@cross_origin()
def get_audio():
    try:
        return send_file('static/audio.wav', mimetype='audio/wav')
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve audio: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)