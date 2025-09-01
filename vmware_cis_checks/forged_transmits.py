import logging
from typing import List, Dict, Any
from pyVmomi import vim

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_forged_transmits(content) -> List[Dict[str, Any]]:
    """检查标准 vSwitch 是否拒绝 Forged Transmits"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            vswitches = host.config.network.vswitch
            for vs in vswitches:
                policy = vs.spec.policy.security
                results.append({
                    "host": host.name,
                    "vswitch": vs.name,
                    "mac_changes": "Accept" if policy.macChanges else "Reject",
                    "promiscuous_mode": "Accept" if policy.allowPromiscuous else "Reject",
                    "forged_transmits": "Accept" if policy.forgedTransmits else "Reject"
                })
                logger.info("主机 %s vSwitch %s ForgedTransmits=%s",
                            host.name, vs.name, policy.forgedTransmits)
        except Exception as e:
            results.append({"host": host.name, "error": str(e)})
            logger.error("主机 %s 获取 vSwitch 安全策略失败: %s", host.name, e)

    container.Destroy()
    return results
