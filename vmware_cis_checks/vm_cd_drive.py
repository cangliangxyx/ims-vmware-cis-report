import os
import logging
from typing import List, Dict
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vm_cd_drive_manual(content=None) -> List[Dict]:
    """
    手工检查：Virtual machines must remove unnecessary CD/DVD devices
    默认通过
    """
    results: List[Dict] = [{
        "AIIB.No": "6.8",
        "Name": "Virtual machines must remove unnecessary CD/DVD devices (Manual)",
        "CIS.No": "7.15",
        "CMD": None,
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认）",
        "Status": "Pass",
        "Description": "VM CD/DVD 设备默认假定已移除不必要设备，需手工验证",
        "Error": None
    }]

    logger.info("[VM CD/DVD Drive] 默认通过检查生成完成")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_6.8_vm_cd_drive_manual.json")

    results = get_vm_cd_drive_manual()
    export_to_json(results, output_path)
    logger.info("[VM CD/DVD Drive] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
