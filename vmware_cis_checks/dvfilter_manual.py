import logging
from typing import List, Dict, Any
from pyVmomi import vim

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_dvfilter(content) -> List[Dict[str, Any]]:
    """获取 dvFilter API 配置 (手工检查是否被限制)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Net.DVFilterBindIpAddress")
            value = adv_settings[0].value if adv_settings else None
            results.append({
                "host": host.name,
                "value": value,
                "description": "dvFilter network API bind IP"
            })
            logger.info("主机 %s dvFilter 配置: %s", host.name, value)
        except Exception as e:
            results.append({"host": host.name, "error": str(e)})
            logger.error("主机 %s 获取 dvFilter 失败: %s", host.name, e)

    container.Destroy()
    return results
