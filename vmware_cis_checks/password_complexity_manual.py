import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_hosts_password_complexity(content=None) -> List[Dict[str, Any]]:
    """
    检查：Host must enforce password complexity (Manual/Automated)
    """
    results = []

    results.append({
        "NO": "2.7",
        "name": "Host must enforce password complexity (Manual)",
        "CIS.NO": "3.11",
        "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select VMHost, Key, Label, Policy, Running, Required',
        "description": "需要人工或脚本验证密码复杂性策略"
    })

    logger.info("检查 2.7: 密码复杂性检查，生成提示")
    return results


def main():
    password_info = get_hosts_password_complexity()
    export_to_json(password_info, "../log/no_2.7_password_complexity.json")


if __name__ == "__main__":
    main()
