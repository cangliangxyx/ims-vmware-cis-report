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
    """获取所有主机的 NTP 配置并增加 Status 字段"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            ntp_servers = host.config.dateTimeInfo.ntpConfig.server or []
            count = len(ntp_servers)

            raw_value = {
                "NTPServers": ntp_servers,
                "Count": count
            }

            results.append({
                "AIIB.No": "1.2",
                "Name": "Host must have reliable time synchronization sources",
                "CIS.No": "2.6",
                "CMD": r'Get-VMHost | Select-Object Name, @{Name="NTPSetting"; Expression={ ($_ | Get-VMHostNtpServer)}}',
                "Host": host.name,
                "Value": raw_value,  # 包含 NTP 列表和数量
                "Status": "Pass" if count >= 2 else "Fail",
                "Description": "检测值: 配置的 NTP 服务器列表, 推荐至少 2 个可靠 NTP 源或使用 PTP 并配置 NTP 备份",
                "Error": None
            })

            logger.info("主机: %s, NTP: %s, Status: %s", host.name, ntp_servers if ntp_servers else "未配置", "Pass" if count >= 2 else "Fail")

        except Exception as e:
            results.append({
                "AIIB.No": "1.2",
                "Name": "Host must have reliable time synchronization sources",
                "CIS.No": "2.6",
                "CMD": r'Get-VMHost | Select-Object Name, @{Name="NTPSetting"; Expression={ ($_ | Get-VMHostNtpServer)}}',
                "Host": host.name,
                "Value": {"NTPServers": [], "Count": 0},
                "Status": "Fail",
                "Description": "NTP server configuration (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 NTP 配置失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_1.2_ntp.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        ntp_info = get_hosts_ntp(content)
        export_to_json(ntp_info, output_path)

if __name__ == "__main__":
    main()
