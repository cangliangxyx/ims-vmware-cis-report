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

def get_hosts_vm_parallel_port(content) -> List[Dict[str, Any]]:
    """获取所有主机下 VM 的 Parallel Port 设备信息"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            vm_values = []
            for vm in host.vm:
                try:
                    parallel_ports = []
                    for device in vm.config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualParallelPort):
                            parallel_ports.append({
                                "Label": getattr(device.deviceInfo, "label", "Unknown"),
                                "Summary": getattr(device.deviceInfo, "summary", "Unknown")
                            })

                    if not parallel_ports:
                        parallel_ports = [{"Label": "ParallelPort", "Summary": "Not Present"}]

                    vm_values.append({
                        "VM": vm.name,
                        "Parallel Ports": parallel_ports
                    })

                except Exception as vm_e:
                    logger.error("主机 %s 的 VM %s 获取 Parallel Port 失败: %s", host.name, vm.name, vm_e)
                    vm_values.append({
                        "VM": vm.name,
                        "Parallel Ports": [{"Label": "Error", "Summary": str(vm_e)}]
                    })

            results.append({
                "AIIB.No": "6.7",
                "Name": "Virtual machines must remove unnecessary parallel port devices (Automated)",
                "CIS.NO": "7.14",
                "CMD": r"Get-VM | Get-ParallelPort",
                "Host": host.name,
                "Value": vm_values,
                "Description": "Check VM Parallel Port devices",
                "Error": None
            })
            logger.info("主机: %s, VM 数量: %d", host.name, len(vm_values))

        except Exception as e:
            results.append({
                "AIIB.No": "6.7",
                "Name": "Virtual machines must remove unnecessary parallel port devices (Automated)",
                "CIS.NO": "7.14",
                "CMD": r"Get-VM | Get-ParallelPort",
                "Host": host.name,
                "Value": [],
                "Description": "Check VM Parallel Port devices (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 VM Parallel Port 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_6.7_vm_parallel_port.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vm_parallel_info = get_hosts_vm_parallel_port(content)
        export_to_json(vm_parallel_info, output_path)


if __name__ == "__main__":
    main()
