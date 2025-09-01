import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_management_networks(content) -> List[Dict[str, Any]]:
    """列出每台主机的管理网络 vmk 接口 (手工检查是否隔离)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            mgmt_vmk = []
            for vnic in host.config.network.vnic:
                if vnic.spec.mgmt:  # 管理网络标记
                    mgmt_vmk.append({
                        "device": vnic.device,
                        "ip": vnic.spec.ip.ipAddress,
                        "subnet_mask": vnic.spec.ip.subnetMask,
                        "portgroup": vnic.portgroup
                    })

            results.append({
                "host": host.name,
                "management_vmk": mgmt_vmk,
                "description": "Management network interfaces (verify isolation manually)"
            })
            logger.info("主机 %s 管理 VMkernel 数: %s", host.name, len(mgmt_vmk))

        except Exception as e:
            results.append({
                "host": host.name,
                "error": str(e)
            })
            logger.error("主机 %s 获取管理网络失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        mgmt_info = get_management_networks(content)
        export_to_json(mgmt_info, "../log/no_4.9_management_network_manual.json")


if __name__ == "__main__":
    main()
