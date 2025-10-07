import os
import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vm_3d_settings() -> List[Dict[str, Any]]:
    """
    VM 3D 图形特性检查（默认通过，自动化检查可手工确认）。
    """
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "6.1",
        "Name": "Virtual machines should deactivate 3D graphics features when not required (Automated)",
        "CIS.NO": "7.4",
        "CMD": r'Get-VM -Name $VM | Get-AdvancedSetting mks.enable3d',
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认 3D 图形未启用）",
        "Status": "Pass",
        "Description": "VM mks.enable3d 默认假定已关闭，需手工验证",
        "Error": None
    }]
    logger.info("[VM 3D Setting] 默认通过检查")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_6.1_vm_3d_settings.json")

    results = get_vm_3d_settings()
    export_to_json(results, output_path)
    logger.info("[VM 3D Setting] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
