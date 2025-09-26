import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_hosts_vm_pci_passthru(content) -> List[Dict[str, Any]]:
    """获取所有主机下 VM 的 PCI/PCIe Passthrough 配置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            vm_values = []
            for vm in host.vm:
                try:
                    passthru_settings = []
                    for opt in vm.config.extraConfig:
                        # 筛选匹配 pciPassthru*.present 的 key
                        if opt.key.startswith("pciPassthru") and opt.key.endswith(".present"):
                            passthru_settings.append({"Name": opt.key, "Value": opt.value})

                    if not passthru_settings:
                        passthru_settings = [{"Name": "pciPassthru*.present", "Value": "Not Configured"}]

                    vm_values.append({
                        "VM": vm.name,
                        "pciPassthru.present": passthru_settings
                    })

                except Exception as vm_e:
                    logger.error("主机 %s 的 VM %s 获取 pciPassthru 配置失败: %s", host.name, vm.name, vm_e)
                    vm_values.append({
                        "VM": vm.name,
                        "pciPassthru.present": [{"Name": "Error", "Value": str(vm_e)}]
                    })

            results.append({
                "AIIB.No": "6.2",
                "Name": "Virtual machines must limit PCI/PCIe device passthrough functionality (Automated)",
                "CIS.NO": "7.7",
                "CMD": r'Get-VM | Get-AdvancedSetting -Name "pciPassthru*.present" | Select Entity,Name,Value',
                "Host": host.name,
                "Value": vm_values,
                "Description": "Check VM PCI/PCIe passthrough settings",
                "Error": None
            })
            logger.info("主机: %s, VM 数量: %d", host.name, len(vm_values))

        except Exception as e:
            results.append({
                "AIIB.No": "6.2",
                "Name": "Virtual machines must limit PCI/PCIe device passthrough functionality (Automated)",
                "CIS.NO": "7.7",
                "CMD": r'Get-VM | Get-AdvancedSetting -Name "pciPassthru*.present" | Select Entity,Name,Value',
                "Host": host.name,
                "Value": [],
                "Description": "Check VM PCI/PCIe passthrough settings (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 VM pciPassthru 配置失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_6.2_vm_pci_passthru.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        pci_passthru_info = get_hosts_vm_pci_passthru(content)
        export_to_json(pci_passthru_info, output_path)

if __name__ == "__main__":
    main()
