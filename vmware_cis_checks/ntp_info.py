# vmware_cis_checks/ntp_info.py

import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)

def get_hosts_ntp(content) -> List[Dict[str, Any]]:
    """获取所有主机的 NTP 配置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            ntp_config = host.config.dateTimeInfo.ntpConfig.server
            results.append({
                "host": host.name,
                "ntp_servers": ntp_config if ntp_config else []
            })
            logger.info("主机: %s, NTP: %s", host.name, ntp_config or "未配置")
        except Exception as e:
            results.append({
                "host": host.name,
                "ntp_servers": [],
                "error": str(e)
            })
            logger.error("主机 %s 获取 NTP 配置失败: %s", host.name, e)

    container.Destroy()
    return results

def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        ntp_info = get_hosts_ntp(content)
        export_to_json(ntp_info, "../log/1.2_ntp_info.json")

if __name__ == "__main__":
    main()
