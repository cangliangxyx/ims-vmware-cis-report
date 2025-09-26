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

def get_hosts_vm_serial_port(content) -> List[Dict[str, Any]]:
    """获取所有主机下 VM 的 Serial Port 设备信息"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            vm_values = []
            for vm in host.vm:
                try:
                    serial_ports = []
                    for device in vm.config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualSerialPort):
                            serial_ports.append({
                                "Label": getattr(device.deviceInfo, "label", "Unknown"),
                                "Summary": getattr(device.deviceInfo, "summary", "Unknown")
                            })

                    if not serial_ports:
                        serial_ports = [{"Label": "SerialPort", "Summary": "Not Present"}]

                    vm_values.append({
                        "VM": vm.name,
                        "Serial Ports": serial_ports
                    })

                except Exception as vm_e:
                    logger.error("主机 %s 的 VM %s 获取 Serial Port 失败: %s", host.name, vm.name, vm_e)
                    vm_values.append({
                        "VM": vm.name,
                        "Serial Ports": [{"Label": "Error", "Summary": str(vm_e)}]
                    })

            results.append({
                "AIIB.No": "6.6",
                "Name": "Virtual machines must remove unnecessary serial port devices (Automated)",
                "CIS.NO": "7.13",
                "CMD": r"Get-VM | Get-SerialPort",
                "Host": host.name,
                "Value": vm_values,
                "Description": "Check VM Serial Port devices",
                "Error": None
            })
            logger.info("主机: %s, VM 数量: %d", host.name, len(vm_values))

        except Exception as e:
            results.append({
                "AIIB.No": "6.6",
                "Name": "Virtual machines must remove unnecessary serial port devices (Automated)",
                "CIS.NO": "7.13",
                "CMD": r"Get-VM | Get-SerialPort",
                "Host": host.name,
                "Value": [],
                "Description": "Check VM Serial Port devices (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 VM Serial Port 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_6.6_vm_serial_port.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vm_serial_info = get_hosts_vm_serial_port(content)
        export_to_json(vm_serial_info, output_path)


if __name__ == "__main__":
    main()
