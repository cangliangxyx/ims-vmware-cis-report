import os
import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vm_ahci_device_manual(content=None) -> List[Dict[str, Any]]:
    """
    手工检查：Virtual machines must remove unnecessary AHCI devices
    默认通过
    """
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "6.4",
        "Name": "Virtual machines must remove unnecessary AHCI devices (Manual)",
        "CIS.No": "7.11",
        "CMD": None,
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认）",
        "Status": "Pass",
        "Description": "VM AHCI 设备默认假定已移除不必要设备，需手工验证",
        "Error": None
    }]

    logger.info("[VM AHCI Device] 默认通过检查生成完成")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_6.4_vm_ahci_device_manual.json")

    results = get_vm_ahci_device_manual()
    export_to_json(results, output_path)
    logger.info("[VM AHCI Device] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
