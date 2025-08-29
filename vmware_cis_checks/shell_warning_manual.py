import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_hosts_shell_warning_manual(content=None) -> List[Dict[str, Any]]:
    """
    手工检查：Host must not suppress warnings that the shell is enabled
    """
    results = []

    results.append({
        "NO": "2.6",
        "name": "Host must not suppress warnings that the shell is enabled (Manual)",
        "CIS.NO": "3.10",
        "cmd": "None",
        "description": "需要人工检查主机是否未抑制 shell 启用警告"
    })

    logger.info("检查 2.6: shell warning 手工检查，无法自动化，已生成提示")
    return results


def main():
    shell_warning_info = get_hosts_shell_warning_manual()
    export_to_json(shell_warning_info, "../log/no_2.6_shell_warning_manual.json")


if __name__ == "__main__":
    main()
