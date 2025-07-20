from flask import Flask, send_from_directory, request, jsonify
import webbrowser
import threading
import os
from engine.command import takeCommand, set_voice_language, processTextCommand, test_command, allCommands

app = Flask(__name__, static_folder="www")

@app.route("/")
def landing():
    return send_from_directory("www", "landing.html")

@app.route("/app")
def assistant():
    return send_from_directory("www/app", "index.html")

@app.route('/app/<path:path>')
def send_app_static(path):
    return send_from_directory('www/app', path)

# Serve any file in www/ at the root (e.g. /landing.css)
@app.route('/<path:filename>')
def serve_www_file(filename):
    if os.path.exists(os.path.join('www', filename)):
        return send_from_directory('www', filename)
    else:
        return "File not found", 404

# --- API ENDPOINTS ---
@app.route('/api/takeCommand', methods=['POST'])
def api_take_command():
    result = takeCommand()
    return jsonify({'result': result})

@app.route('/api/set_voice_language', methods=['POST'])
def api_set_voice_language():
    data = request.get_json()
    lang_code = data.get('lang_code')
    set_voice_language(lang_code)
    return jsonify({'status': 'ok'})

@app.route('/api/processTextCommand', methods=['POST'])
def api_process_text_command():
    data = request.get_json()
    query = data.get('query')
    response = processTextCommand(query)
    return jsonify({'response': response})

@app.route('/api/test_command', methods=['GET'])
def api_test_command():
    result = test_command()
    return jsonify({'result': result})

@app.route('/api/allCommands', methods=['POST'])
def api_all_commands():
    allCommands()
    return jsonify({'status': 'ok'})

def open_browser():
    webbrowser.open_new('http://localhost:8000/')

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(host="0.0.0.0", port=8000, debug=True) 