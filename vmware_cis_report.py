# vmware_cis_report.py
import subprocess
import json, os
from config import settings
from config import commands_list

# 获取服务器配置
vsphere_data = settings.get_vsphere_config(os.getenv('project_env',"prod"))
print(vsphere_data)
BASE_URL = vsphere_data["HOST"]
USERNAME = vsphere_data["USERNAME"]
PASSWORD = vsphere_data["PASSWORD"]
# BASE_URL = vsphere_data["vc-tj-01.vsphere.aiib.org"]
# USERNAME = vsphere_data["psa-infra-pbi@aiib.org"]
# PASSWORD = vsphere_data["8At#q0^BL8T*gx03"]

# 获取执行命令
commands = commands_list.commands_list_def()

def run_powershell(script: str):
    """执行 PowerShell 脚本并返回 stdout/stderr"""
    process = subprocess.Popen(
        ['powershell', '-NoProfile', '-Command', script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8'
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(stderr.strip())
    return stdout.strip(), stderr.strip()

def flatten_obj(obj):
    """递归扁平化 PowerShell 可能产生的复杂对象，防止JSON解析错误"""
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if isinstance(v, dict) and 'Name' in v:
                new_obj[k] = v['Name']
            else:
                new_obj[k] = flatten_obj(v)
        return new_obj
    elif isinstance(obj, list):
        return [flatten_obj(i) for i in obj]
    else:
        return obj

def main():
    ps_parts = [f'Connect-VIServer -Server {BASE_URL} -Protocol https -User "{USERNAME}" -Password "{PASSWORD}"']

    for c in commands:
        if c["cmd"] == 'None':
            # 无需执行命令，写空结果占位
            continue
        ps_parts.append(f'Write-Host "---BEGIN {c["NO"]}---"')
        ps_parts.append(f'{c["cmd"]} | Select-Object * | ConvertTo-Json -Depth 5')
        ps_parts.append(f'Write-Host "---END {c["NO"]}---"')

    ps_script = "\n".join(ps_parts)

    try:
        stdout, stderr = run_powershell(ps_script)
    except Exception as e:
        print("PowerShell 执行异常:", str(e))
        return

    if stderr:
        print("=== PowerShell 错误信息 ===")
        print(stderr)

    results = {}
    current_no = None
    json_buffer = []

    for line in stdout.splitlines():
        if line.startswith("---BEGIN "):
            current_no = line[9:-3]
            json_buffer = []
        elif line.startswith("---END "):
            try:
                raw_json = "\n".join(json_buffer)
                if raw_json.strip():
                    parsed = json.loads(raw_json)
                    results[current_no] = flatten_obj(parsed)
                else:
                    results[current_no] = None
            except json.JSONDecodeError:
                results[current_no] = None
            current_no = None
        elif current_no:
            json_buffer.append(line)

    # 把命令和结果整合，未执行命令也补全None
    combined = []
    for c in commands:
        combined.append({
            "NO": c["NO"],
            "name": c["name"],
            "CIS.NO": c["CIS.NO"],
            "results": results.get(c["NO"], None)
        })

    print(json.dumps(combined, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
