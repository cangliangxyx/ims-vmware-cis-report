import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_vm_ahci_device_manual(content=None) -> List[Dict[str, Any]]:
    """
    手工检查：Virtual machines must remove unnecessary AHCI devices
    """
    results = []

    results.append({
        "AIIB.No": "6.4",
        "Name": "Virtual machines must remove unnecessary AHCI devices (Manual)",
        "CIS.No": "7.11",
        "CMD": None,
        "Host": None,
        "Value": None,
        "Description": "需要人工检查 VM 是否移除不必要的 AHCI 设备",
        "Error": None
    })

    logger.info("检查 6.4: 虚拟机 AHCI 设备手工检查，无法自动化，已生成提示")
    return results


def main(output_dir: str = None):
    """
    手工检查 VM AHCI 设备并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_6.4_vm_ahci_device_manual.json"

    # 获取数据并导出
    vm_ahci_info = get_vm_ahci_device_manual()
    export_to_json(vm_ahci_info, output_path)


if __name__ == "__main__":
    main()
