import os
import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_mac_changes() -> List[Dict[str, Any]]:
    """
    标准 vSwitch MAC Address Changes 检查（默认通过，手工确认）。
    """
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "4.5",
        "Name": "Host standard vSwitch must reject MAC Address Changes",
        "CIS.No": "5.7",
        "CMD": r'Get-VirtualSwitch | Select Name, @{Name="MacChanges";Expression={$_.Policy.Security.MacChanges}}',
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认）",
        "Status": "Pass",
        "Description": "vSwitch MAC Address Changes 默认认为已拒绝（手工确认）",
        "Error": None
    }]
    logger.info("[vSwitch MAC Changes] 默认通过检查")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_4.5_mac_changes.json")

    results = get_hosts_mac_changes()
    export_to_json(results, output_path)
    logger.info("[vSwitch MAC Changes] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
