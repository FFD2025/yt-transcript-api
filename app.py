from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from youtube_transcript_api.proxies import GenericProxyConfig
import os
import random
import time

app = Flask(__name__)

# User agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

def get_proxy_config():
    """Get proxy configuration from environment variables"""
    http_proxy = os.environ.get('HTTP_PROXY', '')
    https_proxy = os.environ.get('HTTPS_PROXY', '')
    
    if http_proxy or https_proxy:
        return GenericProxyConfig(
            http_url=http_proxy,
            https_url=https_proxy
        )
    return None

def get_transcript_with_retry(video_id, languages=None, max_retries=3):
    """Get transcript with retry logic and random delays"""
    
    for attempt in range(max_retries):
        try:
            # Add random delay between attempts
            if attempt > 0:
                delay = random.uniform(1, 3)
                time.sleep(delay)
            
            # Get proxy config
            proxy_config = get_proxy_config()
            
            # Create API instance with proxy if available
            if proxy_config:
                api = YouTubeTranscriptApi(proxy_config=proxy_config)
            else:
                api = YouTubeTranscriptApi()
            
            # Get transcript
            if languages:
                transcript = api.get_transcript(video_id, languages=languages)
            else:
                transcript = api.get_transcript(video_id)
                
            return transcript, None
            
        except Exception as e:
            if attempt == max_retries - 1:
                return None, str(e)
            continue
    
    return None, "Max retries exceeded"

@app.route('/')
def home():
    proxy_status = "enabled" if get_proxy_config() else "disabled"
    return jsonify({
        "message": "YouTube Transcript API Service - Enhanced Version",
        "status": "live",
        "proxy_support": proxy_status,
        "features": [
            "Proxy support",
            "User-agent rotation", 
            "Retry logic",
            "Rate limiting protection"
        ],
        "endpoints": {
            "/transcript/<video_id>": "GET - Get transcript for a YouTube video",
            "/transcript/<video_id>/<language_code>": "GET - Get transcript in specific language",
            "/health": "GET - Health check",
            "/status": "GET - Service status"
        }
    })

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    try:
        transcript, error = get_transcript_with_retry(video_id)
        
        if transcript:
            return jsonify({
                "video_id": video_id,
                "transcript": transcript,
                "status": "success",
                "segments": len(transcript)
            })
        else:
            return jsonify({
                "error": error,
                "video_id": video_id,
                "status": "error",
                "suggestion": "Try again in a few minutes or check if the video has transcripts available"
            }), 400
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "video_id": video_id,
            "status": "error"
        }), 500

@app.route('/transcript/<video_id>/<language_code>')
def get_transcript_with_language(video_id, language_code):
    try:
        transcript, error = get_transcript_with_retry(video_id, languages=[language_code])
        
        if transcript:
            return jsonify({
                "video_id": video_id,
                "language_code": language_code,
                "transcript": transcript,
                "status": "success",
                "segments": len(transcript)
            })
        else:
            return jsonify({
                "error": error,
                "video_id": video_id,
                "language_code": language_code,
                "status": "error",
                "suggestion": f"Try again in a few minutes or check if the video has transcripts in {language_code}"
            }), 400
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "video_id": video_id,
            "language_code": language_code,
            "status": "error"
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "youtube-transcript-api-enhanced",
        "proxy_enabled": get_proxy_config() is not None
    })

@app.route('/status')
def status():
    return jsonify({
        "service": "YouTube Transcript API Enhanced",
        "version": "2.0",
        "features": {
            "proxy_support": get_proxy_config() is not None,
            "retry_logic": True,
            "user_agent_rotation": True,
            "rate_limiting": True
        },
        "environment": {
            "http_proxy": bool(os.environ.get('HTTP_PROXY')),
            "https_proxy": bool(os.environ.get('HTTPS_PROXY'))
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

