from flask import Flask, render_template, jsonify, send_from_directory
import os
import re
from config.vsphere_conn import get_all_hosts_name

app = Flask(__name__)

DEFAULT_HOSTS = [
    'vx-t-esxi-uat08.vsphere.aiib.org', 'vx-t-esxi-uat09.vsphere.aiib.org',
    'vx-t-esxi-uat07.vsphere.aiib.org', 'vx-p-esxi-csz08.vsphere.aiib.org',
    'vx-p-esxi-csz02.vsphere.aiib.org', 'vx-p-esxi-csz04.vsphere.aiib.org',
    'vx-p-esxi-csz01.vsphere.aiib.org', 'vx-p-esxi-csz05.vsphere.aiib.org',
    'vx-p-esxi-csz06.vsphere.aiib.org', 'vx-p-esxi-csz03.vsphere.aiib.org',
    'vx-p-esxi-csz07.vsphere.aiib.org', 'vx-t-esxi-uat03.vsphere.aiib.org',
    'vx-t-esxi-uat02.vsphere.aiib.org', 'vx-t-esxi-uat04.vsphere.aiib.org',
    'vx-t-esxi-uat05.vsphere.aiib.org', 'vx-t-esxi-uat01.vsphere.aiib.org',
    'vx-t-esxi-uat06.vsphere.aiib.org', 'vx-p-esxi-csz10.vsphere.aiib.org',
    'vx-p-esxi-csz09.vsphere.aiib.org', 'vx-p-esxi-csz11.vsphere.aiib.org',
    'vx-p-esxi-csz12.vsphere.aiib.org', 'vx-p-esxi-csz13.vsphere.aiib.org',
    'vx-p-esxi-csz14.vsphere.aiib.org', 'vx-p-esxi-dmz02.vsphere.aiib.org',
    'vx-p-esxi-dmz01.vsphere.aiib.org', 'vx-p-esxi-dmz03.vsphere.aiib.org',
    'vx-p-esxi-vdi03.vsphere.aiib.org', 'vx-p-esxi-vdi02.vsphere.aiib.org',
    'vx-p-esxi-vdi01.vsphere.aiib.org', 'vx-p-esxi-vdi04.vsphere.aiib.org',
    'vx-r-esxi-csz01.vsphere.aiib.org', 'vx-r-esxi-csz04.vsphere.aiib.org',
    'vx-r-esxi-csz03.vsphere.aiib.org', 'vx-r-esxi-csz02.vsphere.aiib.org'
]

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

    def sort_key(f):
        # 提取文件名中的数字部分，例如 no_2.1_ => 2.1
        m = re.search(r'no_(\d+(?:\.\d+)*)_', f)
        if m:
            parts = m.group(1).split('.')
            return tuple(int(p) for p in parts)
        return (0,)  # 如果没有匹配，排在最前面

    return jsonify(sorted(files, key=sort_key))


# 新增 API：返回所有 ESXi 主机名
@app.route('/all_hosts')
def all_hosts():
    return jsonify(DEFAULT_HOSTS)


if __name__ == '__main__':
    app.run(debug=True)
