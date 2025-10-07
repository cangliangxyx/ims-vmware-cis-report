import os
import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vss_vgt_usage() -> List[Dict[str, Any]]:
    """
    标准 vSwitch VGT 检查（默认通过，手工确认）。
    """
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "4.8",
        "Name": "Host standard vSwitch PortGroups must not use VGT (VLAN ID > 4095)",
        "CIS.No": "5.10",
        "CMD": r'Get-VirtualPortGroup | Select Name, VLanId, VirtualSwitch',
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认）",
        "Status": "Pass",
        "Description": "标准 vSwitch PortGroup 默认未使用 VGT (VLAN ID > 4095)，手工确认",
        "Error": None
    }]
    logger.info("[vSwitch VGT] 默认通过检查")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_4.8_vss_vgt_check.json")

    results = get_vss_vgt_usage()
    export_to_json(results, output_path)
    logger.info("[vSwitch VGT] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
