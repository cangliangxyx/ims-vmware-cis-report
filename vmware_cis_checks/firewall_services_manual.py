import logging
from typing import List, Dict, Any
from pyVmomi import vim

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_firewall_services(content) -> List[Dict[str, Any]]:
    """获取每台主机的防火墙服务配置 (手工检查是否限制为授权网段)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            fw_system = host.configManager.firewallSystem
            rules = fw_system.firewallInfo.ruleset
            services = [
                {
                    "name": r.key,
                    "enabled": r.enabled,
                    "allowed_hosts": [ip for ip in (r.allowedHosts.ipAddress or [])]
                }
                for r in rules
            ]
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
