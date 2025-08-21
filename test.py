import subprocess
import json
import os
from config import settings
from config import commands_list

# 获取服务器配置
vsphere_data = settings.get_vsphere_config(os.getenv('project_env', "prod"))
BASE_URL = vsphere_data["HOST"]
USERNAME = vsphere_data["USERNAME"]
PASSWORD = vsphere_data["PASSWORD"]

# 获取执行命令
commands = commands_list.commands_list_def()


def run_powershell(cmd: str):
    """登录 vSphere 并执行单条命令，返回 stdout/stderr"""
    full_cmd = (
        f'Connect-VIServer -Server {BASE_URL} -Protocol https '
        f'-User "{USERNAME}" -Password "{PASSWORD}"; {cmd}'
    )
    process = subprocess.Popen(
        ["powershell", "-NoProfile", "-Command", full_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout.strip(), stderr.strip()


def main():
    results = []

    for c in commands:
        if c["cmd"] == 'None':
            results.append({
                "NO": c["NO"],
                "name": c["name"],
                "CIS.NO": c["CIS.NO"],
                "results": None
            })
            continue

        print(f"[INFO] 执行命令 NO={c['NO']}, name={c['name']}")
        print(f"       CMD: {c['cmd']}")

        code, stdout, stderr = run_powershell(c["cmd"])

        if code != 0 or stderr:
            print(f"[ERROR] 命令执行失败 NO={c['NO']}: {stderr}")
            result_output = None
        else:
            result_output = stdout

        results.append({
            "NO": c["NO"],
            "name": c["name"],
            "CIS.NO": c["CIS.NO"],
            "results": result_output
        })

    # 输出 JSON
    print(json.dumps(results, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
