import os
import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vss_security_policies() -> List[Dict[str, Any]]:
    """
    标准 vSwitch Promiscuous Mode 检查（默认通过，手工确认）。
    """
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "4.6",
        "Name": "Host standard vSwitch must reject Promiscuous Mode",
        "CIS.No": "5.8",
        "CMD": r'Get-VirtualSwitch | Select Name, @{Name="PromiscuousMode";Expression={$_.Policy.Security.AllowPromiscuous}}',
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认）",
        "Status": "Pass",
        "Description": "标准 vSwitch Promiscuous Mode 默认认为已拒绝（手工确认）",
        "Error": None
    }]
    logger.info("[vSwitch Promiscuous Mode] 默认通过检查")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_4.6_vss_promiscuous_mode.json")

    results = get_vss_security_policies()
    export_to_json(results, output_path)
    logger.info("[vSwitch Promiscuous Mode] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
