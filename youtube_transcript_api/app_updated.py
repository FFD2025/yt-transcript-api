from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import os

app = Flask(__name__)

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
        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify({
            "video_id": video_id,
            "transcript": transcript,
            "status": "success"
        })
    except TranscriptsDisabled:
        return jsonify({
            "error": "Transcripts are disabled for this video",
            "video_id": video_id,
            "status": "error"
        }), 400
    except NoTranscriptFound:
        return jsonify({
            "error": "No transcript found for this video",
            "video_id": video_id,
            "status": "error"
        }), 404
    except VideoUnavailable:
        return jsonify({
            "error": "Video is unavailable",
            "video_id": video_id,
            "status": "error"
        }), 404
    except Exception as e:
        return jsonify({
            "error": str(e),
            "video_id": video_id,
            "status": "error"
        }), 500

@app.route('/transcript/<video_id>/<language_code>')
def get_transcript_with_language(video_id, language_code):
    try:
        # Get the transcript in specific language
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        return jsonify({
            "video_id": video_id,
            "language_code": language_code,
            "transcript": transcript,
            "status": "success"
        })
    except TranscriptsDisabled:
        return jsonify({
            "error": "Transcripts are disabled for this video",
            "video_id": video_id,
            "status": "error"
        }), 400
    except NoTranscriptFound:
        return jsonify({
            "error": f"No transcript found for this video in language: {language_code}",
            "video_id": video_id,
            "language_code": language_code,
            "status": "error"
        }), 404
    except VideoUnavailable:
        return jsonify({
            "error": "Video is unavailable",
            "video_id": video_id,
            "status": "error"
        }), 404
    except Exception as e:
        return jsonify({
            "error": str(e),
            "video_id": video_id,
            "language_code": language_code,
            "status": "error"
        }), 500

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # For production deployment (Render will use this)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

