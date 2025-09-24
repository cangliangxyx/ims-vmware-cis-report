import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_hosts_ntp(content) -> List[Dict[str, Any]]:
    """获取所有主机的 NTP 配置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            ntp_config = host.config.dateTimeInfo.ntpConfig.server or []
            results.append({
                "AIIB.No": "1.2",
                "Name": "Host must have reliable time synchronization sources",
                "CIS.NO": "2.6",
                "CMD": r'Get-VMHost | Select-Object Name, @{Name="NTPSetting"; Expression={ ($_ | Get-VMHostNtpServer)}}',
                "Host": host.name,
                "Value": ntp_config,  # 始终是 list
                "Description": "NTP server configuration",
                "Error": None
            })
            logger.info("主机: %s, NTP: %s", host.name, ntp_config if ntp_config else "未配置")

        except Exception as e:
            results.append({
                "AIIB.No": "1.2",
                "Name": "Host must have reliable time synchronization sources",
                "CIS.NO": "2.6",
                "CMD": r'Get-VMHost | Select-Object Name, @{Name="NTPSetting"; Expression={ ($_ | Get-VMHostNtpServer)}}',
                "Host": host.name,
                "Value": [],
                "Description": "NTP server configuration (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 NTP 配置失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        ntp_info = get_hosts_ntp(content)
        export_to_json(ntp_info, "../log/no_1.2_ntp.json")


if __name__ == "__main__":
    main()
