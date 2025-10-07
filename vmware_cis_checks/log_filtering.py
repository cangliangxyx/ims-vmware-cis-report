import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_syslog_log_filtering(content) -> List[Dict[str, Any]]:
    """
    检查所有主机的 Syslog.global.logFiltersEnable 配置，并增加状态字段。
    对应安全基线项：4.5 (L1) Host must deactivate log filtering
    推荐值：False
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logFiltersEnable")

            if adv_settings:
                setting = adv_settings[0]
                value = str(setting.value).strip().lower() if setting.value is not None else ""

                # 状态判断逻辑：推荐值为 False
                if value == "false":
                    status = "Pass"
                else:
                    status = "Fail"

                results.append({
                    "AIIB.No": "3.4",
                    "Name": "Host must deactivate log filtering",
                    "CIS.No": "4.5",
                    "CMD": r"Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logFiltersEnable",
                    "Host": host.name,
                    "Value": value,
                    "Status": status,
                    "Description": (
                        f"检测值: Syslog.global.logFiltersEnable = '{value or '未配置'}' | "
                        "推荐值: False (禁用日志过滤)"
                    ),
                    "Error": None
                })

                logger.info("[Syslog LogFiltering] 主机: %s | 值: %s | 状态: %s",
                            host.name, value or "未配置", status)

            else:
                results.append({
                    "AIIB.No": "3.4",
                    "Name": "Host must deactivate log filtering",
                    "CIS.No": "4.5",
                    "CMD": r"Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logFiltersEnable",
                    "Host": host.name,
                    "Value": None,
                    "Status": "Fail",
                    "Description": "未配置 Syslog.global.logFiltersEnable，建议显式设置为 False。",
                    "Error": None
                })
                logger.warning("[Syslog LogFiltering] 主机 %s 未配置 Syslog.global.logFiltersEnable", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.4",
                "Name": "Host must deactivate log filtering",
                "CIS.No": "4.5",
                "CMD": r"Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logFiltersEnable",
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "该主机不支持 Syslog.global.logFiltersEnable 配置项。",
                "Error": str(e)
            })
            logger.info("[Syslog LogFiltering] 主机 %s 不支持 Syslog.global.logFiltersEnable 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "3.4",
                "Name": "Host must deactivate log filtering",
                "CIS.No": "4.5",
                "CMD": r"Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logFiltersEnable",
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "获取 Syslog.global.logFiltersEnable 失败。",
                "Error": str(e)
            })
            logger.error("[Syslog LogFiltering] 主机 %s 获取 Syslog.global.logFiltersEnable 失败: %s",
                         host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，检查所有主机的 Syslog.global.logFiltersEnable 并导出为 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_3.4_syslog_log_filtering.json")

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
                results = collect_syslog_log_filtering(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[Syslog LogFiltering] 无法连接 vCenter %s: %s", vc_host, e)
            all_results.append({
                "vCenter": vc_host,
                "Host": None,
                "Status": "Fail",
                "Description": "vCenter 连接失败。",
                "Error": str(e)
            })

    export_to_json(all_results, output_path)
    logger.info("[Syslog LogFiltering] 所有主机 Syslog.global.logFiltersEnable 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
