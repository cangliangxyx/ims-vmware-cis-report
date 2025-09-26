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

def get_hosts_vm_cd_drive(content) -> List[Dict[str, Any]]:
    """获取所有主机下 VM 的 CD/DVD 设备信息"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            vm_values = []
            for vm in host.vm:
                try:
                    cd_drives = []
                    for device in vm.config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualCdrom):
                            cd_drives.append({
                                "Label": getattr(device.deviceInfo, "label", "Unknown"),
                                "Summary": getattr(device.deviceInfo, "summary", "Unknown")
                            })

                    if not cd_drives:
                        cd_drives = [{"Label": "CD/DVD Drive", "Summary": "Not Present"}]

                    vm_values.append({
                        "VM": vm.name,
                        "CD/DVD Drives": cd_drives
                    })

                except Exception as vm_e:
                    logger.error("主机 %s 的 VM %s 获取 CD/DVD 设备失败: %s", host.name, vm.name, vm_e)
                    vm_values.append({
                        "VM": vm.name,
                        "CD/DVD Drives": [{"Label": "Error", "Summary": str(vm_e)}]
                    })

            results.append({
                "AIIB.No": "6.8",
                "Name": "Virtual machines must remove unnecessary CD/DVD devices (Automated)",
                "CIS.NO": "7.15",
                "CMD": r"Get-VM | Get-CDDrive",
                "Host": host.name,
                "Value": vm_values,
                "Description": "Check VM CD/DVD drives",
                "Error": None
            })
            logger.info("主机: %s, VM 数量: %d", host.name, len(vm_values))

        except Exception as e:
            results.append({
                "AIIB.No": "6.8",
                "Name": "Virtual machines must remove unnecessary CD/DVD devices (Automated)",
                "CIS.NO": "7.15",
                "CMD": r"Get-VM | Get-CDDrive",
                "Host": host.name,
                "Value": [],
                "Description": "Check VM CD/DVD drives (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 VM CD/DVD 设备失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_6.8_vm_cd_drive.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vm_cd_info = get_hosts_vm_cd_drive(content)
        export_to_json(vm_cd_info, output_path)


if __name__ == "__main__":
    main()
