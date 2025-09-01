import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_tls_log_verify(content) -> List[Dict[str, Any]]:
    """检查是否启用了远程日志 TLS 证书验证"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logCheckCerts")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "host": host.name,
                    "value": setting.value,
                    "type": type(setting.value).__name__,
                    "description": "TLS certificate verification for remote logging"
                })
                logger.info("主机: %s, Syslog.global.logCheckCerts = %s", host.name, setting.value)
            else:
                results.append({
                    "host": host.name,
                    "value": None,
                    "description": "Not configured"
                })
                logger.warning("主机 %s 没有配置 Syslog.global.logCheckCerts", host.name)
        except Exception as e:
            results.append({
                "host": host.name,
                "value": None,
                "error": str(e)
            })
            logger.error("主机 %s 获取 Syslog.global.logCheckCerts 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        tls_log_info = get_hosts_tls_log_verify(content)
        export_to_json(tls_log_info, "../log/no_3.5_tls_log_verify_manual.json")


if __name__ == "__main__":
    main()
