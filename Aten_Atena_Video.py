from flask import Flask, request, jsonify, render_template
import os
import uuid
import logging
import json
import requests
import asyncio
from datetime import datetime
import threading
from werkzeug.utils import secure_filename

# Import VideoSense components for avatar intelligence
try:
    from video_sense import VideoSense, get_video_sense
    from twelvelabs_client import TwelveLabsClient
    VIDEO_INTELLIGENCE_ENABLED = True
except ImportError:
    VIDEO_INTELLIGENCE_ENABLED = False

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Video intelligence configuration
VIDEO_API_BASE = os.getenv("VIDEO_API_BASE", "http://localhost:8000")
API_KEY = os.getenv("MEMNORA_API_KEY", "demo_key_12345")

# Initialize VideoSense if available
if VIDEO_INTELLIGENCE_ENABLED:
    try:
        video_sense = get_video_sense()
        logging.info("VideoSense module initialized successfully")
    except Exception as e:
        logging.warning(f"VideoSense initialization failed: {e}")
        VIDEO_INTELLIGENCE_ENABLED = False

# Configure file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'webm', 'avi', 'mkv'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# In-memory storage for chat history, attachments, and video analyses
chat_histories = {}
attachments_storage = {}
video_analyses = {}
user_profiles = {}

# Enhanced avatar responses with video intelligence
def get_aten_response(user_query, session_id, attachment_info=None, video_analysis=None):
    """Enhanced Aten response with video intelligence integration"""

    # Base responses
    if "hello" in user_query.lower():
        return "Hello there! I'm Aten, enhanced with video intelligence. I can now analyze your videos for behavioral patterns and provide Game of Ten® coaching with visual context."

    if "video" in user_query.lower() or "analyze" in user_query.lower():
        if video_analysis:
            return f"Based on your video analysis: **Posture**: {video_analysis.get('posture_assessment', 'Not detected')}, **Energy**: {video_analysis.get('energy_level', 'Moderate')}, **Focus**: {video_analysis.get('focus_level', 'Neutral')}. Through the Game of Ten® methodology, I recommend focusing on {video_analysis.get('coaching_recommendation', 'mindful presence')}."
        else:
            return "Upload a video and I'll analyze your behavioral patterns through the Game of Ten® lens to provide personalized coaching insights."

    if attachment_info and attachment_info.get('is_video'):
        return f"I've received your video '{attachment_info['filename']}'. Processing through VideoSense for behavioral analysis... This will take a few moments."

    if attachment_info:
        return f"Thanks for the attachment '{attachment_info['filename']}'! I'm analyzing it through the Game of Ten® methodology alongside your query: '{user_query}'."

    return f"Aten received: '{user_query}'. As your true intelligence coach with enhanced video awareness, I'm processing this through the Game of Ten® methodology with deeper contextual understanding."

def get_atena_response(user_query, session_id, attachment_info=None, video_analysis=None):
    """Enhanced Atena response with video intelligence integration"""

    # Base responses
    if "hello" in user_query.lower():
        return "Greetings! I'm Atena, now with video intelligence capabilities. I can analyze your emotional resonance and behavioral patterns through video to provide feminine wisdom through the Memnora Architecture."

    if "video" in user_query.lower() or "emotion" in user_query.lower():
        if video_analysis:
            emotional_state = video_analysis.get('emotional_state', 'neutral')
            resonance_score = video_analysis.get('resonance_score', 0.5)
            return f"Your video shows {emotional_state} emotional resonance with a {resonance_score:.1f} harmony score. Through the Memnora Architecture, I sense {video_analysis.get('emotional_insights', 'growing self-awareness')}. Let me help you balance this energy."
        else:
            return "Share a video with me, and I'll analyze your emotional resonance and behavioral patterns to provide personalized guidance through the Memnora Architecture."

    if attachment_info and attachment_info.get('is_video'):
        return f"I'm receiving your video '{attachment_info['filename']}' with emotional resonance sensitivity. The Memnora Architecture is processing your behavioral patterns and energetic signature..."

    if "memnora architecture" in user_query.lower() or "resonance" in user_query.lower():
        video_context = " with video intelligence integration" if VIDEO_INTELLIGENCE_ENABLED else ""
        return f"The Memnora Architecture{video_context} processes multimodal inputs through resonance matrices. With video analysis, we can now understand your complete behavioral and emotional patterns for deeper harmony."

    if attachment_info:
        return f"Atena received your attachment '{attachment_info['filename']}' along with your query: '{user_query}'. I'm integrating this into my understanding of the Memnora Architecture."

    return f"Atena received: '{user_query}'. I'm engaging with the Memnora Architecture and your video context to provide harmonized emotional resonance guidance."

def analyze_video_behavioral_patterns(video_analysis_result):
    """Extract behavioral patterns from video analysis for avatar coaching"""

    if not video_analysis_result:
        return None

    patterns = {
        'posture_assessment': 'balanced',
        'energy_level': 'moderate',
        'focus_level': 'attentive',
        'emotional_state': 'neutral',
        'resonance_score': 0.7,
        'coaching_recommendation': 'maintain current practice',
        'emotional_insights': 'stable presence detected'
    }

    # Analyze resonance vector if available
    if video_analysis_result.get('resonance_vector'):
        vector = video_analysis_result['resonance_vector']
        if len(vector) >= 9:
            # Emotional dimensions (6-9)
            emotional_avg = sum(vector[6:9]) / 4
            if emotional_avg > 0.7:
                patterns['emotional_state'] = 'positive and uplifted'
                patterns['emotional_insights'] = 'high positive energy and joy detected'
            elif emotional_avg < 0.3:
                patterns['emotional_state'] = 'contemplative and focused'
                patterns['emotional_insights'] = 'deep concentration and introspection present'

            patterns['resonance_score'] = (emotional_avg + 1) / 2  # Normalize to 0-1

    # Analyze temporal patterns
    if video_analysis_result.get('temporal_patterns'):
        temporal = video_analysis_result['temporal_patterns']
        scene_count = temporal.get('scene_count', 1)

        if scene_count > 10:
            patterns['focus_level'] = 'dynamically engaged'
            patterns['energy_level'] = 'high and varied'
        elif scene_count < 3:
            patterns['focus_level'] = 'deeply concentrated'
            patterns['energy_level'] = 'steady and consistent'

    # Analyze speech patterns if available
    if video_analysis_result.get('speech_patterns'):
        speech = video_analysis_result['speech_patterns']
        energy = speech.get('energy_level', 0.5)

        if energy > 0.7:
            patterns['coaching_recommendation'] = 'channel energy into focused expression'
        elif energy < 0.3:
            patterns['coaching_recommendation'] = 'gentle movement and breath work suggested'

    return patterns

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video_async(video_path, video_id, session_id):
    """Background processing of video analysis"""
    try:
        if not VIDEO_INTELLIGENCE_ENABLED:
            # Mock analysis for demo
            import time
            time.sleep(2)  # Simulate processing time

            video_analyses[video_id] = {
                'status': 'completed',
                'mock_analysis': True,
                'summary': 'Demo video analysis completed',
                'posture_assessment': 'upright and confident',
                'energy_level': 'balanced and present',
                'focus_level': 'attentive and engaged',
                'emotional_state': 'positive and receptive',
                'resonance_score': 0.75,
                'coaching_recommendation': 'continue current practice with increased awareness'
            }
            return

        # Real video analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            resonance_payload = loop.run_until_complete(
                video_sense.analyze_video_file(video_path)
            )

            behavioral_patterns = analyze_video_behavioral_patterns(
                resonance_payload.__dict__
            )

            video_analyses[video_id] = {
                'status': 'completed',
                'resonance_payload': resonance_payload.__dict__,
                'behavioral_patterns': behavioral_patterns,
                'summary': resonance_payload.metadata.get('summary', 'Video analyzed successfully') if resonance_payload.metadata else 'Analysis complete'
            }

        except Exception as e:
            logging.error(f"Video analysis failed: {e}")
            video_analyses[video_id] = {
                'status': 'failed',
                'error': str(e)
            }
        finally:
            loop.close()

    except Exception as e:
        logging.error(f"Video processing error: {e}")
        video_analyses[video_id] = {
            'status': 'failed',
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/unified-chat', methods=['POST'])
def unified_chat():
    avatar = request.headers.get('X-Avatar')
    user_query = request.form.get('user_query', '')
    session_id = request.form.get('session_id')
    attachment = request.files.get('attachment')

    if not session_id:
        session_id = str(uuid.uuid4())
        logging.info(f"New session created: {session_id}")

    attachment_info = None
    video_analysis = None

    # Handle file attachments
    if attachment:
        filename = secure_filename(attachment.filename)

        # Check if it's a video file
        is_video = allowed_file(filename)

        if is_video:
            # Save video file
            video_id = str(uuid.uuid4())
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{video_id}_{filename}")
            attachment.save(video_path)

            # Store video info
            attachment_info = {
                'id': video_id,
                'filename': filename,
                'content_type': attachment.content_type,
                'is_video': True,
                'video_id': video_id
            }

            # Start background video analysis
            video_analyses[video_id] = {'status': 'processing'}
            thread = threading.Thread(
                target=process_video_async,
                args=(video_path, video_id, session_id)
            )
            thread.daemon = True
            thread.start()

            logging.info(f"Video '{filename}' uploaded for analysis (ID: {video_id})")

        else:
            # Handle non-video attachments
            attachment_id = str(uuid.uuid4())
            attachments_storage[attachment_id] = {
                'filename': filename,
                'content_type': attachment.content_type,
                'size': len(attachment.read()),
                'session_id': session_id,
                'avatar': avatar,
                'is_video': False
            }
            attachment.seek(0)
            attachment_info = {'id': attachment_id, 'filename': filename, 'is_video': False}
            logging.info(f"Attachment '{filename}' uploaded for session {session_id} by {avatar}.")

    # Check for existing video analysis results
    if attachment_info and attachment_info.get('video_id'):
        video_id = attachment_info['video_id']
        if video_id in video_analyses and video_analyses[video_id]['status'] == 'completed':
            video_analysis = video_analyses[video_id].get('behavioral_patterns')

    # Get or initialize chat history for the session
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    # Add user message to history
    chat_histories[session_id].append({
        'sender': 'user',
        'message': user_query,
        'attachment': attachment_info
    })

    # Generate avatar response with video intelligence
    response_text = ""
    if avatar == 'aten':
        response_text = get_aten_response(user_query, session_id, attachment_info, video_analysis)
    elif avatar == 'atena':
        response_text = get_atena_response(user_query, session_id, attachment_info, video_analysis)
    else:
        response_text = "Invalid avatar specified."
        logging.warning(f"Invalid avatar '{avatar}' received for session {session_id}.")

    # Add avatar response to history
    chat_histories[session_id].append({'sender': avatar, 'message': response_text})
    logging.info(f"Session {session_id} - {avatar} response: {response_text[:50]}...")

    return jsonify({
        'response': response_text,
        'session_id': session_id,
        'video_analysis_status': video_analyses[attachment_info.get('video_id', '')]['status'] if attachment_info and attachment_info.get('video_id') in video_analyses else None
    })

@app.route('/api/video-analysis/<video_id>', methods=['GET'])
def get_video_analysis_status(video_id):
    """Get video analysis status and results"""
    if video_id not in video_analyses:
        return jsonify({'error': 'Video not found'}), 404

    return jsonify(video_analyses[video_id])

@app.route('/api/video-upload', methods=['POST'])
def upload_video_direct():
    """Direct video upload endpoint for external integrations"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(video.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    video_id = str(uuid.uuid4())
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{video_id}_{filename}")
    video.save(video_path)

    # Start analysis
    video_analyses[video_id] = {'status': 'processing'}
    thread = threading.Thread(
        target=process_video_async,
        args=(video_path, video_id, None)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'video_id': video_id,
        'filename': filename,
        'status': 'uploading',
        'message': 'Video uploaded successfully for analysis'
    })

# Enhanced HTML template with video upload capabilities
def create_enhanced_template():
    """Create enhanced HTML template with video upload features"""
    html_content = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aten & Atena - Video Intelligence Coaching | Memnora</title>
    <style>
        /* Base styles from original */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'inter', -apple-system, sans-serif;
            background: #0a0e1b;
            color: #ffffff;
            height: 100vh;
            overflow: hidden;
        }

        /* header */
        .header {
            background: rgba(10, 14, 27, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 255, 255, 0.3);
            height: 70px;
        }

        .header-title {
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(90deg, #00ffff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .video-badge {
            background: linear-gradient(135deg, #00ff88, #00a8cc);
            color: #0a0e1b;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 15px;
        }

        .nav-buttons {
            display: flex;
            gap: 15px;
        }

        .nav-btn {
            padding: 10px 20px;
            background: transparent;
            border: 1px solid rgba(0, 255, 255, 0.3);
            color: #00ffff;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
        }

        .nav-btn:hover {
            background: rgba(0, 255, 255, 0.1);
        }

        /* main container */
        .split-container {
            display: flex;
            height: calc(100vh - 70px);
        }

        /* avatar panels */
        .avatar-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .aten-panel {
            background: linear-gradient(135deg, #0a1628 0%, #1a2844 100%);
            border-right: 1px solid rgba(0, 255, 255, 0.2);
        }

        .atena-panel {
            background: linear-gradient(135deg, #1a0a28 0%, #2a1844 100%);
        }

        /* avatar header */
        .avatar-header {
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            gap: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .avatar-image {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
        }

        .aten-panel .avatar-image {
            border: 2px solid #00ffff;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }

        .atena-panel .avatar-image {
            border: 2px solid #ff00ff;
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.5);
        }

        .avatar-info {
            flex: 1;
        }

        .avatar-name {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .aten-panel .avatar-name {
            color: #00ffff;
        }

        .atena-panel .avatar-name {
            color: #ff00ff;
        }

        .avatar-status {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
        }

        .video-indicator {
            background: linear-gradient(135deg, #00ff88, #00a8cc);
            color: #0a0e1b;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7rem;
            font-weight: bold;
            margin-left: 10px;
        }

        /* emotional resonance bar */
        .emotional-bar {
            height: 4px;
            background: rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }

        .emotional-wave {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, currentcolor, transparent);
            animation: wave 2s linear infinite;
        }

        .aten-panel .emotional-wave {
            color: #00ffff;
        }

        .atena-panel .emotional-wave {
            color: #ff00ff;
        }

        @keyframes wave {
            0% { transform: translatex(-100%); }
            100% { transform: translatex(100%); }
        }

        /* chat messages */
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            padding: 15px;
            border-radius: 10px;
            max-width: 80%;
            animation: messagein 0.3s ease;
        }

        @keyframes messagein {
            from {
                opacity: 0;
                transform: translatey(10px);
            }
            to {
                opacity: 1;
                transform: translatey(0);
            }
        }

        .message-user {
            align-self: flex-end;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .aten-panel .message-avatar {
            align-self: flex-start;
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid rgba(0, 255, 255, 0.3);
        }

        .atena-panel .message-avatar {
            align-self: flex-start;
            background: rgba(255, 0, 255, 0.1);
            border: 1px solid rgba(255, 0, 255, 0.3);
        }

        .video-analysis-result {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            font-size: 0.9rem;
        }

        .video-analysis-result h4 {
            color: #00ff88;
            margin-bottom: 8px;
        }

        .video-analysis-result .pattern {
            margin: 4px 0;
        }

        .video-analysis-result .pattern-label {
            color: #00ffff;
            font-weight: bold;
        }

        /* input section */
        .input-section {
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .input-wrapper {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .attachment-btn {
            width: 45px;
            height: 45px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            color: #fff;
            font-size: 1.2rem;
            position: relative;
        }

        .attachment-btn.video-enabled {
            background: linear-gradient(135deg, #00ff88, #00a8cc);
            color: #0a0e1b;
            font-weight: bold;
        }

        .attachment-btn:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .aten-panel .attachment-btn:hover {
            border-color: #00ffff;
        }

        .atena-panel .attachment-btn:hover {
            border-color: #ff00ff;
        }

        .chat-input {
            flex: 1;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            color: #fff;
            font-size: 1rem;
        }

        .aten-panel .chat-input:focus {
            outline: none;
            border-color: #00ffff;
        }

        .atena-panel .chat-input:focus {
            outline: none;
            border-color: #ff00ff;
        }

        .send-btn {
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }

        .aten-panel .send-btn {
            background: linear-gradient(135deg, #00ffff, #00a8cc);
            color: #0a0e1b;
        }

        .atena-panel .send-btn {
            background: linear-gradient(135deg, #ff00ff, #cc00cc);
            color: #0a0e1b;
        }

        .send-btn:hover {
            transform: scale(1.05);
        }

        /* attachment preview */
        .attachment-preview {
            display: none;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            margin-bottom: 10px;
            align-items: center;
            justify-content: space-between;
        }

        .attachment-preview.active {
            display: flex;
        }

        .attachment-preview.video-preview {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
        }

        .attachment-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .video-status {
            font-size: 0.8rem;
            color: #00ff88;
            margin-left: 10px;
        }

        .remove-attachment {
            cursor: pointer;
            color: #ff4444;
        }

        /* typing indicator */
        .typing-indicator {
            display: none;
            padding: 10px;
            align-self: flex-start;
        }

        .typing-indicator.active {
            display: block;
        }

        .typing-dots {
            display: flex;
            gap: 5px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: currentcolor;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .aten-panel .typing-dot {
            background: #00ffff;
        }

        .atena-panel .typing-dot {
            background: #ff00ff;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translatey(0);
                opacity: 0.5;
            }
            30% {
                transform: translatey(-10px);
                opacity: 1;
            }
        }

        /* mobile responsive */
        @media (max-width: 768px) {
            .split-container {
                flex-direction: column;
            }
        }

        /* file input styling */
        input[type="file"] {
            display: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">
            split-screen chat - aten & atena
            <span class="video-badge">VIDEO INTELLIGENCE</span>
        </div>
        <div class="nav-buttons">
            <a href="/" class="nav-btn">home</a>
            <a href="/coach" class="nav-btn">single coach</a>
            <a href="/modules" class="nav-btn">modules</a>
        </div>
    </div>

    <div class="split-container">
        <div class="avatar-panel aten-panel">
            <div class="avatar-header">
                <img src="/static/avatar-aten.png" alt="aten" class="avatar-image">
                <div class="avatar-info">
                    <div class="avatar-name">
                        aten
                        <span class="video-indicator">AI</span>
                    </div>
                    <div class="avatar-status">true intelligence coach • game of ten® • video analysis</div>
                </div>
            </div>
            <div class="emotional-bar">
                <div class="emotional-wave"></div>
            </div>

            <div class="chat-messages" id="atenmessages">
                <div class="message message-avatar">
                    welcome! i'm aten, enhanced with video intelligence. i can now analyze your videos for behavioral patterns and provide game of ten® coaching with visual context. upload a video to get started!
                </div>
            </div>

            <div class="typing-indicator" id="atentyping">
                <div class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>

            <div class="input-section">
                <div class="attachment-preview" id="atenattachmentpreview">
                    <div class="attachment-info">
                        <span>📹</span>
                        <span id="atenattachmentname"></span>
                        <span class="video-status" id="atenvideostatus"></span>
                    </div>
                    <span class="remove-attachment" onclick="removeAttachment('aten')">✕</span>
                </div>
                <div class="input-wrapper">
                    <button class="attachment-btn video-enabled" onclick="document.getElementById('atenfileinput').click()" title="Upload video for analysis">
                        📹
                    </button>
                    <input type="file" id="atenfileinput" accept="video/mp4,video/quicktime,video/webm,video/x-msvideo">
                    <input type="text" class="chat-input" id="ateninput" placeholder="ask aten about your video analysis...">
                    <button class="send-btn" onclick="sendToAten()">send</button>
                </div>
            </div>
        </div>

        <div class="avatar-panel atena-panel">
            <div class="avatar-header">
                <img src="/static/avatar-atena.png" alt="atena" class="avatar-image">
                <div class="avatar-info">
                    <div class="avatar-name">
                        atena
                        <span class="video-indicator">AI</span>
                    </div>
                    <div class="avatar-status">true intelligence coach • memnora architecture • emotional resonance</div>
                </div>
            </div>
            <div class="emotional-bar">
                <div class="emotional-wave"></div>
            </div>

            <div class="chat-messages" id="atenamessages">
                <div class="message message-avatar">
                    hello! i'm atena, now with video intelligence capabilities. i can analyze your emotional resonance and behavioral patterns through video to provide feminine wisdom through the memnora architecture. share a video with me!
                </div>
            </div>

            <div class="typing-indicator" id="atenatyping">
                <div class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>

            <div class="input-section">
                <div class="attachment-preview" id="atenaattachmentpreview">
                    <div class="attachment-info">
                        <span>📹</span>
                        <span id="atenaattachmentname"></span>
                        <span class="video-status" id="atenavideostatus"></span>
                    </div>
                    <span class="remove-attachment" onclick="removeAttachment('atena')">✕</span>
                </div>
                <div class="input-wrapper">
                    <button class="attachment-btn video-enabled" onclick="document.getElementById('atenafileinput').click()" title="Upload video for emotional analysis">
                        📹
                    </button>
                    <input type="file" id="atenafileinput" accept="video/mp4,video/quicktime,video/webm,video/x-msvideo">
                    <input type="text" class="chat-input" id="atenainput" placeholder="ask atena about emotional analysis...">
                    <button class="send-btn" onclick="sendToAtena()">send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let atenSession = 'aten_' + Date.now();
        let atenaSession = 'atena_' + Date.now();
        let atenAttachment = null;
        let atenaAttachment = null;

        // Enhanced file handling for video
        function setupFileHandler(avatar) {
            const fileInput = document.getElementById(avatar + 'fileinput');
            const attachmentName = document.getElementById(avatar + 'attachmentname');
            const attachmentPreview = document.getElementById(avatar + 'attachmentpreview');
            const videoStatus = document.getElementById(avatar + 'videostatus');

            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    if (avatar === 'aten') {
                        atenAttachment = file;
                    } else {
                        atenaAttachment = file;
                    }

                    attachmentName.textContent = file.name;
                    attachmentPreview.classList.add('active', 'video-preview');
                    videoStatus.textContent = 'Processing...';

                    // Start checking video analysis status
                    if (file.type.startsWith('video/')) {
                        checkVideoStatus(file.name, avatar);
                    }
                }
            });
        }

        function checkVideoStatus(filename, avatar) {
            const videoStatus = document.getElementById(avatar + 'videostatus');

            // Simulate processing status updates
            let status = 'Analyzing video...';
            const statuses = [
                'Analyzing video...',
                'Extracting behavioral patterns...',
                'Calculating emotional resonance...',
                'Generating coaching insights...'
            ];

            let statusIndex = 0;
            const statusInterval = setInterval(() => {
                if (statusIndex < statuses.length) {
                    videoStatus.textContent = statuses[statusIndex];
                    statusIndex++;
                } else {
                    videoStatus.textContent = 'Analysis complete';
                    clearInterval(statusInterval);
                }
            }, 2000);
        }

        function removeAttachment(avatar) {
            if (avatar === 'aten') {
                atenAttachment = null;
            } else {
                atenaAttachment = null;
            }

            const attachmentPreview = document.getElementById(avatar + 'attachmentpreview');
            const fileInput = document.getElementById(avatar + 'fileinput');

            attachmentPreview.classList.remove('active', 'video-preview');
            fileInput.value = '';
        }

        async function sendToAvatar(avatar) {
            const input = document.getElementById(avatar + 'input');
            const typingIndicator = document.getElementById(avatar + 'typing');
            const messagesContainer = document.getElementById(avatar + 'messages');

            const message = input.value.trim();
            if (!message) return;

            const attachment = avatar === 'aten' ? atenAttachment : atenaAttachment;
            const sessionId = avatar === 'aten' ? atenSession : atenaSession;

            // Add user message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'message message-user';
            userMessageDiv.textContent = message;
            if (attachment) {
                userMessageDiv.innerHTML += `<br><small>📹 ${attachment.name}</small>`;
            }
            messagesContainer.appendChild(userMessageDiv);

            // Show typing indicator
            typingIndicator.classList.add('active');

            try {
                const formData = new FormData();
                formData.append('user_query', message);
                formData.append('session_id', sessionId);
                if (attachment) {
                    formData.append('attachment', attachment);
                }

                const response = await fetch('/api/unified-chat', {
                    method: 'POST',
                    headers: {
                        'X-Avatar': avatar
                    },
                    body: formData
                });

                const data = await response.json();

                // Hide typing indicator
                typingIndicator.classList.remove('active');

                // Add avatar response
                const avatarMessageDiv = document.createElement('div');
                avatarMessageDiv.className = 'message message-avatar';

                // Parse markdown-style bold text
                let responseText = data.response.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
                avatarMessageDiv.innerHTML = responseText;

                // Add video analysis results if available
                if (data.video_analysis_status === 'completed') {
                    const analysisDiv = document.createElement('div');
                    analysisDiv.className = 'video-analysis-result';
                    analysisDiv.innerHTML = `
                        <h4>🎬 Video Analysis Complete</h4>
                        <div class="pattern">
                            <span class="pattern-label">Coaching Insights:</span>
                            Behavioral patterns analyzed successfully
                        </div>
                    `;
                    avatarMessageDiv.appendChild(analysisDiv);
                }

                messagesContainer.appendChild(avatarMessageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                // Clear input and attachment
                input.value = '';
                if (attachment) {
                    removeAttachment(avatar);
                }

            } catch (error) {
                console.error('Error sending message:', error);
                typingIndicator.classList.remove('active');

                const errorDiv = document.createElement('div');
                errorDiv.className = 'message message-avatar';
                errorDiv.textContent = 'Sorry, there was an error processing your request. Please try again.';
                messagesContainer.appendChild(errorDiv);
            }
        }

        function sendToAten() {
            sendToAvatar('aten');
        }

        function sendToAtena() {
            sendToAvatar('atena');
        }

        // Enter key support
        document.getElementById('ateninput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendToAten();
            }
        });

        document.getElementById('atenainput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendToAtena();
            }
        });

        // Initialize file handlers
        setupFileHandler('aten');
        setupFileHandler('atena');
    </script>
</body>
</html>
    """

    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Write enhanced template
    with open('templates/index.html', 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    # Create enhanced template
    create_enhanced_template()

    # Run Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)