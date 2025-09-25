import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_management_networks(content) -> List[Dict[str, Any]]:
    """列出每台主机的管理网络 VMkernel 接口 (手工检查是否隔离)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            mgmt_vmk = []
            for vnic in host.config.network.vnic:
                if getattr(vnic.spec, "mgmt", False):  # 管理网络标记
                    mgmt_vmk.append({
                        "device": vnic.device,
                        "ip": getattr(vnic.spec.ip, "ipAddress", None),
                        "subnet_mask": getattr(vnic.spec.ip, "subnetMask", None),
                        "portgroup": vnic.portgroup
                    })

            results.append({
                "AIIB.No": "4.9",
                "Name": "Host management network interfaces must be isolated",
                "CIS.No": "5.11",
                "CMD": r'Get-VMHostNetworkAdapter | Where-Object {$_.ManagementTraffic -eq $true} | Select Name, IP, SubnetMask, PortGroup',
                "Host": host.name,
                "Value": mgmt_vmk,
                "Description": "Management network interfaces (verify isolation manually)",
                "Error": None
            })
            logger.info("主机 %s 管理 VMkernel 数: %s", host.name, len(mgmt_vmk))

        except Exception as e:
            results.append({
                "AIIB.No": "4.9",
                "Name": "Host management network interfaces must be isolated",
                "CIS.No": "5.11",
                "CMD": r'Get-VMHostNetworkAdapter | Where-Object {$_.ManagementTraffic -eq $true} | Select Name, IP, SubnetMask, PortGroup',
                "Host": host.name,
                "Value": None,
                "Description": "Management network retrieval error",
                "Error": str(e)
            })
            logger.error("主机 %s 获取管理网络失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查所有主机管理网络 VMkernel 接口并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_4.9_management_network_manual.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        mgmt_info = get_management_networks(content)
        export_to_json(mgmt_info, output_path)


if __name__ == "__main__":
    main()
