import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

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
                "Value": raw_value,
                "Status": "Pass" if count >= 2 else "Fail",
                "Description": "检测值: 配置的 NTP 服务器列表, 推荐至少 2 个可靠 NTP 源或使用 PTP 并配置 NTP 备份",
                "Error": None
            })

            logger.info(
                "主机: %s, NTP: %s, Status: %s",
                host.name,
                ntp_servers if ntp_servers else "未配置",
                "Pass" if count >= 2 else "Fail"
            )

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
    """循环多个 vCenter，按主机拆分 NTP 配置并单独存为 JSON 文件"""
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)

    # 获取 vCenter host 列表
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data["HOST"]
    if not isinstance(host_list, list):
        host_list = [host_list]

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                ntp_info = get_hosts_ntp(content)

                # 按每台 ESXi 主机拆分文件
                for host_entry in ntp_info:
                    hostname = host_entry["Host"]
                    json_path = os.path.join(output_dir, f"no_1.2_{hostname}_ntp.json")
                    export_to_json([host_entry], json_path)
                    logger.info("主机 %s 的 NTP 配置已导出到 %s", hostname, json_path)

        except Exception as e:
            logger.error("连接 vCenter %s 失败: %s", vc_host, e)


if __name__ == "__main__":
    main()
