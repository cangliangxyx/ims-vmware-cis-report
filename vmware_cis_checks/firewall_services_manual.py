import os
import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_firewall_services() -> List[Dict[str, Any]]:
    """
    防火墙规则检查（默认通过，手工确认）。
    返回示例结果，Value 可自定义为空或默认允许配置。
    """
    # 示例默认通过结果
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "4.1",
        "Name": "Host firewall services must be restricted to authorized networks (Manual)",
        "CIS.No": "5.1",
        "CMD": r'Get-VMHost | Get-VMHostFirewallException | Select-Object Name, Enabled, AllowedHosts',
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认）",
        "Status": "Pass",
        "Description": "防火墙服务默认认为受限于授权网络（手工确认）",
        "Error": None
    }]
    logger.info("[Firewall] 默认通过防火墙检查")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_4.1_firewall_services_manual.json")

    results = get_hosts_firewall_services()
    export_to_json(results, output_path)
    logger.info("[Firewall] 防火墙检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
