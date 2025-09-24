import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_syslog_info_level(content) -> List[Dict[str, Any]]:
    """获取每台主机的 Syslog.global.logLevel 配置（只读）"""
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
                    "Name": "Syslog logging level (Read Only)",
                    "CIS.No": "4.4",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logLevel',
                    "Host": host.name,
                    "Value": setting.value,
                    "Description": "Syslog logging level",
                    "Error": None
                })
                logger.info("主机: %s, Syslog.global.logLevel = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "3.3",
                    "Name": "Syslog logging level (Read Only)",
                    "CIS.No": "4.4",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logLevel',
                    "Host": host.name,
                    "Value": None,
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Syslog.global.logLevel", host.name)
        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.3",
                "Name": "Syslog logging level (Read Only)",
                "CIS.No": "4.3",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logLevel',
                "Host": host.name,
                "Value": None,
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Syslog.global.logLevel 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "3.3",
                "Name": "Syslog logging level (Read Only)",
                "CIS.No": "4.4",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logLevel',
                "Host": host.name,
                "Value": None,
                "Description": "Error retrieving syslog log level",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Syslog.global.logLevel 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        loglevel_info = get_hosts_syslog_info_level(content)
        export_to_json(loglevel_info, "../log/no_3.3_syslog_info_level_manual.json")


if __name__ == "__main__":
    main()
