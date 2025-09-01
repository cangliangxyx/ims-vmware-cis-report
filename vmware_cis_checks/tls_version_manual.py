import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_tls_version(content) -> List[Dict[str, Any]]:
    """获取每台主机的 TLS 配置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            # VMware ESXi 高级设置: UserVars.ESXiVPsTLSConfig 或类似
            adv_settings = host.configManager.advancedOption.QueryOptions("UserVars.ESXiVPsTLSConfig")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "host": host.name,
                    "value": setting.value,
                    "type": type(setting.value).__name__,
                    "description": "TLS protocol configuration"
                })
                logger.info("主机: %s, TLS Config = %s", host.name, setting.value)
            else:
                results.append({
                    "host": host.name,
                    "value": None,
                    "description": "Not configured"
                })
                logger.warning("主机 %s 没有配置 TLS 设置", host.name)
        except Exception as e:
            results.append({
                "host": host.name,
                "value": None,
                "error": str(e)
            })
            logger.error("主机 %s 获取 TLS 设置失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        tls_info = get_hosts_tls_version(content)
        export_to_json(tls_info, "../log/no_2.16_tls_version_manual.json")


if __name__ == "__main__":
    main()
