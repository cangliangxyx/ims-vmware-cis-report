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

def get_hosts_vm_floppy_drive(content) -> List[Dict[str, Any]]:
    """获取所有主机下 VM 的 Floppy 设备信息"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            vm_values = []
            for vm in host.vm:
                try:
                    floppy_drives = []
                    for device in vm.config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualFloppy):
                            connection_state = getattr(device.connectable, "connected", None)
                            floppy_drives.append({
                                "Label": getattr(device.deviceInfo, "label", "Unknown"),
                                "Summary": getattr(device.deviceInfo, "summary", "Unknown"),
                                "Connected": connection_state
                            })

                    if not floppy_drives:
                        floppy_drives = [{"Label": "Floppy", "Summary": "Not Present", "Connected": False}]

                    vm_values.append({
                        "VM": vm.name,
                        "Floppy Drives": floppy_drives
                    })

                except Exception as vm_e:
                    logger.error("主机 %s 的 VM %s 获取 Floppy 设备失败: %s", host.name, vm.name, vm_e)
                    vm_values.append({
                        "VM": vm.name,
                        "Floppy Drives": [{"Label": "Error", "Summary": str(vm_e), "Connected": None}]
                    })

            results.append({
                "AIIB.No": "6.9",
                "Name": "Virtual machines must remove unnecessary floppy devices (Automated)",
                "CIS.NO": "7.16",
                "CMD": r"Get-VM | Get-FloppyDrive | Select Parent, Name, ConnectionState",
                "Host": host.name,
                "Value": vm_values,
                "Description": "Check VM Floppy drives",
                "Error": None
            })
            logger.info("主机: %s, VM 数量: %d", host.name, len(vm_values))

        except Exception as e:
            results.append({
                "AIIB.No": "6.9",
                "Name": "Virtual machines must remove unnecessary floppy devices (Automated)",
                "CIS.NO": "7.16",
                "CMD": r"Get-VM | Get-FloppyDrive | Select Parent, Name, ConnectionState",
                "Host": host.name,
                "Value": [],
                "Description": "Check VM Floppy drives (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 VM Floppy 设备失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_6.9_vm_floppy_drive.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vm_floppy_info = get_hosts_vm_floppy_drive(content)
        export_to_json(vm_floppy_info, output_path)


if __name__ == "__main__":
    main()
