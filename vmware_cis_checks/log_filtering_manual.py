import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_log_filtering(content) -> List[Dict[str, Any]]:
    """检查是否启用了日志过滤 (Syslog.global.logFilters, 只读)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logFilters")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "3.4",
                    "Name": "Syslog log filtering configuration (Read Only)",
                    "CIS.No": "4.5",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logFilters',
                    "Host": host.name,
                    "Value": setting.value,
                    "Description": "Syslog log filtering configuration",
                    "Error": None
                })
                logger.info("主机: %s, Syslog.global.logFilters = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "3.4",
                    "Name": "Syslog log filtering configuration (Read Only)",
                    "CIS.No": "4.5",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logFilters',
                    "Host": host.name,
                    "Value": None,
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Syslog.global.logFilters", host.name)
        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.4",
                "Name": "Syslog log filtering configuration (Read Only)",
                "CIS.No": "4.5",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logFilters',
                "Host": host.name,
                "Value": None,
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Syslog.global.logFilters 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "3.4",
                "Name": "Syslog log filtering configuration (Read Only)",
                "CIS.No": "4.5",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logFilters',
                "Host": host.name,
                "Value": None,
                "Description": "Error retrieving log filtering setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Syslog.global.logFilters 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查主机日志过滤配置并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    # 设置默认输出目录
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_3.4_log_filtering_manual.json"

    # 获取数据并导出
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        logfilter_info = get_hosts_log_filtering(content)
        export_to_json(logfilter_info, output_path)


if __name__ == "__main__":
    main()
