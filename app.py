from flask import Flask, render_template, jsonify, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log/<path:filename>')
def serve_log(filename):
    return send_from_directory('log', filename)

@app.route('/log_files')
def log_files():
    log_dir = 'log'
    files = [f"/log/{f}" for f in os.listdir(log_dir) if f.endswith('.json')]
    return jsonify(sorted(files))

if __name__ == '__main__':
    app.run(debug=True)
