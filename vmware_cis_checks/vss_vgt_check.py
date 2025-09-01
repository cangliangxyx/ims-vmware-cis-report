import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vss_vgt_usage(content) -> List[Dict[str, Any]]:
    """检查标准 vSwitch 上是否有 PortGroup 使用 VGT (VLAN ID > 4095)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            vgt_pg = []
            for pg in host.config.network.portgroup:
                if pg.spec.vlanId > 4095:  # VGT
                    vgt_pg.append({
                        "portgroup": pg.spec.name,
                        "vswitch": pg.spec.vswitchName,
                        "vlan_id": pg.spec.vlanId
                    })

            results.append({
                "host": host.name,
                "vgt_portgroups": vgt_pg,
                "description": "PortGroups using Virtual Guest Tagging (VGT)"
            })
            logger.info("主机 %s VGT 端口组数: %s", host.name, len(vgt_pg))

        except Exception as e:
            results.append({
                "host": host.name,
                "error": str(e)
            })
            logger.error("主机 %s 获取 VGT 配置失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vgt_info = get_vss_vgt_usage(content)
        export_to_json(vgt_info, "../log/no_4.8_vss_vgt_check.json")


if __name__ == "__main__":
    main()
