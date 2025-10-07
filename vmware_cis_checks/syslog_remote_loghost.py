import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_syslog_remote_loghost(content) -> List[Dict[str, Any]]:
    """
    检查所有主机的 Syslog.global.logHost 配置（远程日志服务器）并增加状态字段。
    对应安全基线项：4.2 Host must transmit system logs to a remote log collector
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logHost")
            if adv_settings:
                setting = adv_settings[0]
                value = setting.value.strip() if setting.value else ""
                # 状态判断：若为空或仅有 "localhost"，视为 Fail
                if value and not value.lower().startswith("8.102"):
                    status = "Pass"
                else:
                    status = "Fail"

                results.append({
                    "AIIB.No": "3.2",
                    "Name": "Host must transmit system logs to a remote log collector",
                    "CIS.No": "4.2",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logHost',
                    "Host": host.name,
                    "Value": value,
                    "Status": status,
                    "Description": (
                        "检测值: Syslog.global.logHost={} | 推荐配置远程日志主机地址，如 udp://10.100.8.102:514 "
                        "监测方法是否包含8.102"
                    ).format(value or "未配置"),
                    "Error": None
                })

                logger.info("[Syslog] 主机: %s | Syslog.global.logHost = %s | Status = %s",
                            host.name, value or "未配置", status)

            else:
                results.append({
                    "AIIB.No": "3.2",
                    "Name": "Host must transmit system logs to a remote log collector",
                    "CIS.No": "4.2",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logHost',
                    "Host": host.name,
                    "Value": None,
                    "Status": "Fail",
                    "Description": "未配置 Syslog.global.logHost，建议配置远程日志服务器",
                    "Error": None
                })
                logger.warning("[Syslog] 主机 %s 未配置 Syslog.global.logHost", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.2",
                "Name": "Host must transmit system logs to a remote log collector",
                "CIS.No": "4.2",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logHost',
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "该主机不支持 Syslog.global.logHost 配置",
                "Error": str(e)
            })
            logger.info("[Syslog] 主机 %s 不支持 Syslog.global.logHost 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "3.2",
                "Name": "Host must transmit system logs to a remote log collector",
                "CIS.No": "4.2",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logHost',
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "获取 Syslog.global.logHost 配置失败",
                "Error": str(e)
            })
            logger.error("[Syslog] 主机 %s 获取 Syslog.global.logHost 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查所有 vCenter 的主机 Syslog.global.logHost 配置并导出为 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_3.2_syslog_remote_loghost.json")

    # 读取 vCenter 列表
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_syslog_remote_loghost(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[Syslog] 无法连接 vCenter %s: %s", vc_host, e)

    # 导出统一 JSON
    export_to_json(all_results, output_path)
    logger.info("[Syslog] 所有主机 Syslog.global.logHost 配置已导出到 %s", output_path)


if __name__ == "__main__":
    main()
