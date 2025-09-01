import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_firewall_services(content) -> List[Dict[str, Any]]:
    """获取每台主机的防火墙服务配置 (手工检查是否限制为授权网段)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            fw_system = host.configManager.firewallSystem
            rules = fw_system.firewallInfo.ruleset

            services = []
            for r in rules:
                allowed = []
                if r.allowedHosts:
                    if r.allowedHosts.allIp:
                        allowed = ["All"]  # 表示允许所有
                    elif r.allowedHosts.ipAddress:
                        allowed = list(r.allowedHosts.ipAddress)

                services.append({
                    "name": r.key,
                    "enabled": r.enabled,
                    "allowed_hosts": allowed
                })

            results.append({
                "host": host.name,
                "services": services,
                "description": "Firewall services and allowed networks"
            })
            logger.info("主机 %s 防火墙规则数: %s", host.name, len(services))

        except Exception as e:
            results.append({
                "host": host.name,
                "error": str(e)
            })
            logger.error("主机 %s 获取防火墙服务失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        fw_info = get_hosts_firewall_services(content)
        export_to_json(fw_info, "../log/no_4.1_firewall_services_manual.json")


if __name__ == "__main__":
    main()
