import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_vm_hardware_version_manual(content=None) -> List[Dict[str, Any]]:
    """
    手工检查：Virtual machines should have virtual machine hardware version 19 or newer
    """
    results = []

    results.append({
        "AIIB.No": "6.10",
        "Name": "Virtual machines should have virtual machine hardware version 19 or newer (Manual)",
        "CIS.No": "7.29",
        "CMD": None,
        "Host": None,
        "Value": None,
        "Description": "需要人工检查 VM 是否使用硬件版本 19 或更高版本",
        "Error": None
    })

    logger.info("检查 6.10: VM 硬件版本手工检查，无法自动化，已生成提示")
    return results


def main(output_dir: str = None):
    """
    手工检查 VM 硬件版本并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_6.10_vm_hardware_version_manual.json"

    vm_hw_info = get_vm_hardware_version_manual()
    export_to_json(vm_hw_info, output_path)


if __name__ == "__main__":
    main()
