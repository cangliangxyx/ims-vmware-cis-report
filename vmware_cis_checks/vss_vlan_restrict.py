import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vss_portgroup_vlans(content) -> List[Dict[str, Any]]:
    """获取标准虚拟交换机端口组 VLAN ID"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            pg_info = []
            for pg in host.config.network.portgroup:
                pg_info.append({
                    "portgroup": pg.spec.name,
                    "vswitch": pg.spec.vswitchName,
                    "vlan_id": pg.spec.vlanId
                })

            results.append({
                "host": host.name,
                "portgroups": pg_info,
                "description": "Standard vSwitch PortGroup VLAN configuration"
            })
            logger.info("主机 %s PortGroup 数: %s", host.name, len(pg_info))

        except Exception as e:
            results.append({
                "host": host.name,
                "error": str(e)
            })
            logger.error("主机 %s 获取 PortGroup VLAN 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vlan_info = get_vss_portgroup_vlans(content)
        export_to_json(vlan_info, "../log/no_4.7_vss_vlan_restrict.json")


if __name__ == "__main__":
    main()
