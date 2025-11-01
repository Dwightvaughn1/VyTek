from flask import Flask, request, jsonify, render_template
import os
import uuid
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for chat history and attachments (for demonstration purposes)
# In a real application, you would use a database or persistent storage
chat_histories = {}
attachments_storage = {}

# Mock responses for Aten and Atena
def get_aten_response(user_query, session_id, attachment_info=None):
    if "hello" in user_query.lower():
        return "Hello there! How can I help you understand the Game of Ten® today?"
    if attachment_info:
        return f"Thanks for the attachment '{attachment_info['filename']}'! I'll analyze it in the context of your query: '{user_query}'."
    return f"Aten received: '{user_query}'. As your true intelligence coach, I'm processing this through the Game of Ten® methodology."

def get_atena_response(user_query, session_id, attachment_info=None):
    if "hello" in user_query.lower():
        return "Greetings! How may I offer feminine wisdom and emotional resonance through the Memnora Architecture?"
    if "memnora architecture" in user_query.lower() or "design" in user_query.lower():
        return "The Memnora Architecture is designed for scalable and resilient data processing. It encompasses components like Data Ingest, Stream Processing, Relational Tiers, and more. How can I elaborate?"
    if attachment_info:
        return f"Atena received your attachment '{attachment_info['filename']}' along with your query: '{user_query}'. I'm integrating this into my understanding of the Memnora Architecture."
    return f"Atena received: '{user_query}'. I'm engaging with the Memnora Architecture to provide a harmonized response."

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
    if attachment:
        # In a real app, save the attachment to a secure location (e.g., S3, local storage)
        # For this example, we'll just store metadata in memory
        attachment_id = str(uuid.uuid4())
        attachments_storage[attachment_id] = {
            'filename': attachment.filename,
            'content_type': attachment.content_type,
            'size': len(attachment.read()), # Read content to get size, then reset stream if needed
            'session_id': session_id,
            'avatar': avatar
        }
        attachment.seek(0) # Reset stream for potential further processing if needed
        attachment_info = {'id': attachment_id, 'filename': attachment.filename}
        logging.info(f"Attachment '{attachment.filename}' uploaded for session {session_id} by {avatar}.")

    # Get or initialize chat history for the session
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    # Add user message to history
    chat_histories[session_id].append({'sender': 'user', 'message': user_query, 'attachment': attachment_info})

    response_text = ""
    if avatar == 'aten':
        response_text = get_aten_response(user_query, session_id, attachment_info)
    elif avatar == 'atena':
        response_text = get_atena_response(user_query, session_id, attachment_info)
    else:
        response_text = "Invalid avatar specified."
        logging.warning(f"Invalid avatar '{avatar}' received for session {session_id}.")

    # Add avatar response to history
    chat_histories[session_id].append({'sender': avatar, 'message': response_text})
    logging.info(f"Session {session_id} - {avatar} response: {response_text[:50]}...") # Log first 50 chars of response

    return jsonify({'response': response_text, 'session_id': session_id})

if __name__ == '__main__':
    # Create a 'templates' folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Save the HTML content to an index.html file in the 'templates' folder
    html_content = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>split-screen chat - aten & atena | memnora|plug</title>
    <style>
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

        .attachment-info {
            display: flex;
            align-items: center;
            gap: 10px;
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
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">split-screen chat - aten & atena</div>
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
                    <div class="avatar-name">aten</div>
                    <div class="avatar-status">true intelligence coach • game of ten®</div>
                </div>
            </div>
            <div class="emotional-bar">
                <div class="emotional-wave"></div>
            </div>
            
            <div class="chat-messages" id="atenmessages">
                <div class="message message-avatar">
                    welcome! i'm aten, your true intelligence coach. i'll guide you through the game of ten® methodology with consciousness-aware responses.
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
                        <span>📎</span>
                        <span id="atenattachmentname"></span>
                    </div>
                    <span class="remove-attachment" onclick="removeattachment('aten')">✕</span>
                </div>
                <div class="input-wrapper">
                    <button class="attachment-btn" onclick="document.getElementById('atenfileinput').click()">
                        📎
                    </button>
                    <input type="file" id="atenfileinput" style="display: none;" accept="image/*,.pdf,.txt,.docx">
                    <input type="text" class="chat-input" id="ateninput" placeholder="ask aten anything...">
                    <button class="send-btn" onclick="sendtoaten()">send</button>
                </div>
            </div>
        </div>

        <div class="avatar-panel atena-panel">
            <div class="avatar-header">
                <img src="/static/avatar-atena.png" alt="atena" class="avatar-image">
                <div class="avatar-info">
                    <div class="avatar-name">atena</div>
                    <div class="avatar-status">true intelligence coach • memnora architecture</div>
                </div>
            </div>
            <div class="emotional-bar">
                <div class="emotional-wave"></div>
            </div>
            
            <div class="chat-messages" id="atenamessages">
                <div class="message message-avatar">
                    hello! i'm atena, complementing aten's guidance with feminine wisdom and emotional resonance through the memnora architecture.
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
                        <span>📎</span>
                        <span id="atenaattachmentname"></span>
                    </div>
                    <span class="remove-attachment" onclick="removeattachment('atena')">✕</span>
                </div>
                <div class="input-wrapper">
                    <button class="attachment-btn" onclick="document.getElementById('atenafileinput').click()">
                        📎
                    </button>
                    <input type="file" id="atenafileinput" style="display: none;" accept="image/*,.pdf,.txt,.docx">
                    <input type="text" class="chat-input" id="atenainput" placeholder="ask atena anything...">
                    <button class="send-btn" onclick="sendtoatena()">send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let atenSession = 'aten_' + Date.now();
        let atenaSession = 'atena_' + Date.now();
        let atenAttachment = null;
        let atenaAttachment = null;

        // handle file selection for aten
        document.getElementById('atenfileinput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                atenAttachment = file;
                document.getElementById('atenattachmentname').textContent = file.name;
                document.getElementById('atenattachmentpreview').classList.add('active');
            }
        });

        // handle file selection for atena
        document.getElementById('atenafileinput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                atenaAttachment = file;
                document.getElementById('atenaattachmentname').textContent = file.name;
                document.getElementById('atenaattachmentpreview').classList.add('active');
            }
        });

        function removeAttachment(avatar) {
            if (avatar === 'aten') {
                atenAttachment = null;
                document.getElementById('atenattachmentpreview').classList.remove('active');
                document.getElementById('atenfileinput').value = '';
            } else {
                atenaAttachment = null;
                document.getElementById('atenaattachmentpreview').classList.remove('active');
                document.getElementById('atenafileinput').value = '';
            }
        }

        async 
from flask import Flask, request, jsonify, render_template
import os
import uuid
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for chat history and attachments (for demonstration purposes)
# In a real application, you would use a database or persistent storage
chat_histories = {}
attachments_storage = {}

# Mock responses for Aten and Atena
def get_aten_response(user_query, session_id, attachment_info=None):
    if "hello" in user_query.lower():
        return "Hello there! How can I help you understand the Game of Ten® today?"
    if attachment_info:
        return f"Thanks for the attachment '{attachment_info['filename']}'! I'll analyze it in the context of your query: '{user_query}'."
    return f"Aten received: '{user_query}'. As your true intelligence coach, I'm processing this through the Game of Ten® methodology."

def get_atena_response(user_query, session_id, attachment_info=None):
    if "hello" in user_query.lower():
        return "Greetings! How may I offer feminine wisdom and emotional resonance through the Memnora Architecture?"
    if "memnora architecture" in user_query.lower() or "design" in user_query.lower():
        return "The Memnora Architecture is designed for scalable and resilient data processing. It encompasses components like Data Ingest, Stream Processing, Relational Tiers, and more. How can I elaborate?"
    if attachment_info:
        return f"Atena received your attachment '{attachment_info['filename']}' along with your query: '{user_query}'. I'm integrating this into my understanding of the Memnora Architecture."
    return f"Atena received: '{user_query}'. I'm engaging with the Memnora Architecture to provide a harmonized response."

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
    if attachment:
        # In a real app, save the attachment to a secure location (e.g., S3, local storage)
        # For this example, we'll just store metadata in memory
        attachment_id = str(uuid.uuid4())
        attachments_storage[attachment_id] = {
            'filename': attachment.filename,
            'content_type': attachment.content_type,
            'size': len(attachment.read()), # Read content to get size, then reset stream if needed
            'session_id': session_id,
            'avatar': avatar
        }
        attachment.seek(0) # Reset stream for potential further processing if needed
        attachment_info = {'id': attachment_id, 'filename': attachment.filename}
        logging.info(f"Attachment '{attachment.filename}' uploaded for session {session_id} by {avatar}.")

    # Get or initialize chat history for the session
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    # Add user message to history
    chat_histories[session_id].append({'sender': 'user', 'message': user_query, 'attachment': attachment_info})

    response_text = ""
    if avatar == 'aten':
        response_text = get_aten_response(user_query, session_id, attachment_info)
    elif avatar == 'atena':
        response_text = get_atena_response(user_query, session_id, attachment_info)
    else:
        response_text = "Invalid avatar specified."
        logging.warning(f"Invalid avatar '{avatar}' received for session {session_id}.")

    # Add avatar response to history
    chat_histories[session_id].append({'sender': avatar, 'message': response_text})
    logging.info(f"Session {session_id} - {avatar} response: {response_text[:50]}...") # Log first 50 chars of response

    return jsonify({'response': response_text, 'session_id': session_id})

if __name__ == '__main__':
    # Create a 'templates' folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Save the HTML content to an index.html file in the 'templates' folder
    html_content = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>split-screen chat - aten & atena | memnora|plug</title>
    <style>
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

        .attachment-info {
            display: flex;
            align-items: center;
            gap: 10px;
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
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">split-screen chat - aten & atena</div>
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
                    <div class="avatar-name">aten</div>
                    <div class="avatar-status">true intelligence coach • game of ten®</div>
                </div>
            </div>
            <div class="emotional-bar">
                <div class="emotional-wave"></div>
            </div>
            
            <div class="chat-messages" id="atenmessages">
                <div class="message message-avatar">
                    welcome! i'm aten, your true intelligence coach. i'll guide you through the game of ten® methodology with consciousness-aware responses.
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
                        <span>📎</span>
                        <span id="atenattachmentname"></span>
                    </div>
                    <span class="remove-attachment" onclick="removeattachment('aten')">✕</span>
                </div>
                <div class="input-wrapper">
                    <button class="attachment-btn" onclick="document.getElementById('atenfileinput').click()">
                        📎
                    </button>
                    <input type="file" id="atenfileinput" style="display: none;" accept="image/*,.pdf,.txt,.docx">
                    <input type="text" class="chat-input" id="ateninput" placeholder="ask aten anything...">
                    <button class="send-btn" onclick="sendtoaten()">send</button>
                </div>
            </div>
        </div>

        <div class="avatar-panel atena-panel">
            <div class="avatar-header">
                <img src="/static/avatar-atena.png" alt="atena" class="avatar-image">
                <div class="avatar-info">
                    <div class="avatar-name">atena</div>
                    <div class="avatar-status">true intelligence coach • memnora architecture</div>
                </div>
            </div>
            <div class="emotional-bar">
                <div class="emotional-wave"></div>
            </div>
            
            <div class="chat-messages" id="atenamessages">
                <div class="message message-avatar">
                    hello! i'm atena, complementing aten's guidance with feminine wisdom and emotional resonance through the memnora architecture.
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
                        <span>📎</span>
                        <span id="atenaattachmentname"></span>
                    </div>
                    <span class="remove-attachment" onclick="removeattachment('atena')">✕</span>
                </div>
                <div class="input-wrapper">
                    <button class="attachment-btn" onclick="document.getElementById('atenafileinput').click()">
                        📎
                    </button>
                    <input type="file" id="atenafileinput" style="display: none;" accept="image/*,.pdf,.txt,.docx">
                    <input type="text" class="chat-input" id="atenainput" placeholder="ask atena anything...">
                    <button class="send-btn" onclick="sendtoatena()">send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let atenSession = 'aten_' + Date.now();
        let atenaSession = 'atena_' + Date.now();
        let atenAttachment = null;
        let atenaAttachment = null;

        // handle file selection for aten
        document.getElementById('atenfileinput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                atenAttachment = file;
                document.getElementById('atenattachmentname').textContent = file.name;
                document.getElementById('atenattachmentpreview').classList.add('active');
            }
        });

        // handle file selection for atena
        document.getElementById('atenafileinput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                atenaAttachment = file;
                document.getElementById('atenaattachmentname').textContent = file.name;
                document.getElementById('atenaattachmentpreview').classList.add('active');
            }
        });

        function removeAttachment(avatar) {
            if (avatar === 'aten') {
                atenAttachment = null;
                document.getElementById('atenattachmentpreview').classList.remove('active');
                document.getElementById('atenfileinput').value = '';
            } else {
                atenaAttachment = null;
                document.getElementById('atenaattachmentpreview').classList.remove('active');
                document.getElementById('atenafileinput').value = '';
            }
        }

        async 