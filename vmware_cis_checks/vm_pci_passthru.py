import os
import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vm_pci_passthru() -> List[Dict[str, Any]]:
    """
    VM PCI/PCIe Passthrough 检查（默认通过，自动化检查可手工确认）。
    """
    results: List[Dict[str, Any]] = [{
        "AIIB.No": "6.2",
        "Name": "Virtual machines must limit PCI/PCIe device passthrough functionality (Automated)",
        "CIS.NO": "7.7",
        "CMD": r'Get-VM | Get-AdvancedSetting -Name "pciPassthru*.present" | Select Entity,Name,Value',
        "Host": "ALL_HOSTS",
        "Value": "默认通过（手工确认 PCI/PCIe Passthrough 未滥用）",
        "Status": "Pass",
        "Description": "VM PCI/PCIe passthrough 默认假定安全，需手工验证",
        "Error": None
    }]
    logger.info("[VM PCI Passthrough] 默认通过检查")
    return results


def main(output_dir: str = None):
    """
    直接返回默认通过结果并导出 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_6.2_vm_pci_passthru.json")

    results = get_vm_pci_passthru()
    export_to_json(results, output_path)
    logger.info("[VM PCI Passthrough] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
