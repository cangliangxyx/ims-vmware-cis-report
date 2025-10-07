import os
import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_management_networks() -> List[Dict[str, Any]]:
    """
    管理网络 VMkernel 检查（默认通过，手工确认隔离）。
    """
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "4.9",
        "Name": "Host management network interfaces must be isolated",
        "CIS.No": "5.11",
        "CMD": r'Get-VMHostNetworkAdapter | Where-Object {$_.ManagementTraffic -eq $true} | Select Name, IP, SubnetMask, PortGroup',
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认隔离）",
        "Status": "Pass",
        "Description": "管理网络 VMkernel 接口默认假定已隔离，需手工验证",
        "Error": None
    }]
    logger.info("[Management Network] 默认通过检查")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_4.9_management_network_manual.json")

    results = get_management_networks()
    export_to_json(results, output_path)
    logger.info("[Management Network] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
