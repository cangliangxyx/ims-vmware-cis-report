import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_syslog_info_level(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的 Syslog.global.logLevel 配置（只读）
    :param content: vSphere API content 对象
    :return: 包含每台主机 Syslog.global.logLevel 的列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logLevel")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "3.3",
                    "Name": "Syslog Logging Level (Read Only)",
                    "CIS.No": "4.4",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logLevel',
                    "Host": host.name,
                    "Value": {"key": setting.key, "value": setting.value, "type": type(setting.value).__name__},
                    "Description": "Syslog logging level 配置，建议 INFO 或更高。",
                    "Error": None
                })
                logger.info("主机 %s Syslog.global.logLevel = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "3.3",
                    "Name": "Syslog Logging Level (Read Only)",
                    "CIS.No": "4.4",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logLevel',
                    "Host": host.name,
                    "Value": {"key": "Syslog.global.logLevel", "value": None, "type": None},
                    "Description": "未配置 Syslog 日志级别，可能使用默认值",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Syslog.global.logLevel", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.3",
                "Name": "Syslog Logging Level (Read Only)",
                "CIS.No": "4.4",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logLevel',
                "Host": host.name,
                "Value": None,
                "Description": "该主机不支持 Syslog.global.logLevel 设置",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Syslog.global.logLevel 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "3.3",
                "Name": "Syslog Logging Level (Read Only)",
                "CIS.No": "4.4",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logLevel',
                "Host": host.name,
                "Value": None,
                "Description": "查询 Syslog.global.logLevel 失败",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Syslog.global.logLevel 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查主机 Syslog.global.logLevel 并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_3.3_syslog_info_level.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        syslog_info = get_hosts_syslog_info_level(content)
        export_to_json(syslog_info, output_path)
        logger.info("Syslog.global.logLevel 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
