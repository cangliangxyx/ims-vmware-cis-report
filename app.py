from flask import Flask, render_template, send_from_directory, jsonify
import os

app = Flask(__name__, static_folder='log')

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 返回 log 目录下 JSON 文件列表
@app.route('/log_files')
def log_files():
    files = [f for f in os.listdir(LOG_DIR) if f.endswith('.json')]
    # 返回前端可直接 fetch 的完整路径
    file_paths = [f"/log/{f}" for f in files]
    return jsonify(file_paths)

# 静态文件路由（JSON 文件）
@app.route('/log/<path:filename>')
def serve_log(filename):
    return send_from_directory(LOG_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
