import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vss_security_policies(content) -> List[Dict[str, Any]]:
    """获取标准虚拟交换机的安全策略 (混杂模式、MAC 修改、伪造传输)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            network_system = host.configManager.networkSystem
            vss_list = [v for v in network_system.networkConfig.vswitch]

            vss_info = []
            for vss in vss_list:
                sec = vss.spec.policy.security
                vss_info.append({
                    "vswitch": vss.name,
                    "promiscuous_mode": "Accept" if sec.allowPromiscuous else "Reject",
                    "mac_changes": "Accept" if sec.macChanges else "Reject",
                    "forged_transmits": "Accept" if sec.forgedTransmits else "Reject",
                })

            results.append({
                "host": host.name,
                "vswitches": vss_info,
                "description": "Standard vSwitch security policies"
            })
            logger.info("主机 %s vSwitch 数: %s", host.name, len(vss_info))

        except Exception as e:
            results.append({
                "host": host.name,
                "error": str(e)
            })
            logger.error("主机 %s 获取 vSwitch 配置失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vss_info = get_vss_security_policies(content)
        export_to_json(vss_info, "../log/no_4.6_vss_promiscuous_mode.json")


if __name__ == "__main__":
    main()
