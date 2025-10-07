import os
import logging
from typing import List, Dict
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vm_hardware_version_manual(content=None) -> List[Dict[str, Any]]:
    """
    手工检查：Virtual machines should have virtual machine hardware version 19 or newer
    默认通过
    """
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "6.10",
        "Name": "Virtual machines should have virtual machine hardware version 19 or newer (Manual)",
        "CIS.No": "7.29",
        "CMD": None,
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认）",
        "Status": "Pass",
        "Description": "VM 硬件版本默认假定符合要求，需人工验证",
        "Error": None
    }]

    logger.info("[VM Hardware Version] 默认通过检查生成完成")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_6.10_vm_hardware_version_manual.json")

    results = get_vm_hardware_version_manual()
    export_to_json(results, output_path)
    logger.info("[VM Hardware Version] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
