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

def get_hosts_vm_usb_settings(content) -> List[Dict[str, Any]]:
    """获取所有主机下 VM 的 USB/XHCI 设备信息"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            vm_values = []
            for vm in host.vm:
                try:
                    usb_devices = []
                    for device in vm.config.hardware.device:
                        # 筛选 USB 设备
                        if isinstance(device, vim.vm.device.VirtualUSB):
                            usb_devices.append({
                                "Label": getattr(device, "deviceInfo", {}).get("label", "Unknown"),
                                "Summary": getattr(device, "deviceInfo", {}).get("summary", "Unknown")
                            })

                    if not usb_devices:
                        usb_devices = [{"Label": "USB/XHCI", "Summary": "Not Present"}]

                    vm_values.append({
                        "VM": vm.name,
                        "USB/XHCI Devices": usb_devices
                    })

                except Exception as vm_e:
                    logger.error("主机 %s 的 VM %s 获取 USB/XHCI 设备失败: %s", host.name, vm.name, vm_e)
                    vm_values.append({
                        "VM": vm.name,
                        "USB/XHCI Devices": [{"Label": "Error", "Summary": str(vm_e)}]
                    })

            results.append({
                "AIIB.No": "6.5",
                "Name": "Virtual machines must remove unnecessary USB/XHCI devices (Automated)",
                "CIS.NO": "7.12",
                "CMD": r"Get-VM | Get-USBDevice",
                "Host": host.name,
                "Value": vm_values,
                "Description": "Check VM USB/XHCI devices",
                "Error": None
            })
            logger.info("主机: %s, VM 数量: %d", host.name, len(vm_values))

        except Exception as e:
            results.append({
                "AIIB.No": "6.5",
                "Name": "Virtual machines must remove unnecessary USB/XHCI devices (Automated)",
                "CIS.NO": "7.12",
                "CMD": r"Get-VM | Get-USBDevice",
                "Host": host.name,
                "Value": [],
                "Description": "Check VM USB/XHCI devices (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 VM USB/XHCI 设备失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_6.5_vm_usb_xhci_devices.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vm_usb_info = get_hosts_vm_usb_settings(content)
        export_to_json(vm_usb_info, output_path)


if __name__ == "__main__":
    main()
