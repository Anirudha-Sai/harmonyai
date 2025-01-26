from flask import Flask, request, jsonify, send_file, render_template
import base64
import numpy as np
import soundfile as sf
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__, static_folder='frontend', template_folder='frontend')
CORS(app, resources={r"/*": {"origins": "*"}})

colab_ngrok_url = None  # Global variable to store the Colab ngrok URL

@app.route('/')
def serve_frontend():
    """Serve the frontend HTML file."""
    return render_template('index.html')

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
    app.run()
