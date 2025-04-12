from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import requests
from datetime import timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

JAMENDO_CLIENT_ID = "fb9fa6e3"  # Replace with your real key

@app.route("/generate_playlist", methods=["POST"])
def generate_playlist():
    data = request.json
    mood = data.get("mood", "")
    genre = data.get("genre", "")
    instrument = data.get("instrument", "")
    duration = int(data.get("duration", 30))

    # Build query
    tags = [mood]
    if genre:
        tags.append(genre)
    tag_query = ",".join(tags)
    instrumental = True if instrument else False

    url = (
        f"https://api.jamendo.com/v3.0/tracks/?client_id={JAMENDO_CLIENT_ID}"
        f"&format=json&limit=100&fuzzytags={tag_query}&audioformat=mp31&order=popularity_total"
        f"{'&instrumental=1' if instrumental else ''}"
    )

    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        tracks = data.get("results", [])

        playlist = []
        total_duration = 0
        max_duration = duration * 60

        for track in tracks:
            dur = track["duration"]
            if total_duration + dur <= max_duration:
                playlist.append(track)
                total_duration += dur
            if total_duration >= max_duration:
                break

        return jsonify({
            "success": True,
            "total_duration": str(timedelta(seconds=total_duration)),
            "tracks": playlist
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=3002)
