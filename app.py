from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, static_folder='log')

# 首页路由
@app.route('/')
def index():
    # 渲染 index.html
    return render_template('index.html')

# 静态文件路由（JSON 文件）
@app.route('/log/<path:filename>')
def serve_log(filename):
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
    return send_from_directory(log_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
