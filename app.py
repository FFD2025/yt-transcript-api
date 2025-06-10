from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import os

app = Flask(__name__ )

@app.route('/')
def home():
    return jsonify({
        "message": "YouTube Transcript API Service",
        "endpoints": {
            "/transcript/<video_id>": "GET - Get transcript for a YouTube video",
            "/transcript/<video_id>/<language_code>": "GET - Get transcript in specific language"
        }
    })

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify({
            "video_id": video_id,
            "transcript": transcript,
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "video_id": video_id,
            "status": "error"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
