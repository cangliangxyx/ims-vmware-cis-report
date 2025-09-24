import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_syslog_persistent(content) -> List[Dict[str, Any]]:
    """查看每台主机的 Syslog.global.logDir 配置（只读）"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logDir")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "3.1",
                    "Name": "Persistent Syslog Configuration (Read Only)",
                    "CIS.No": "4.1",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                    "Host": host.name,
                    "Value": setting.value,
                    "Description": "Persistent syslog directory",
                    "Error": None
                })
                logger.info("主机: %s, Syslog.global.logDir = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "3.1",
                    "Name": "Persistent Syslog Configuration (Read Only)",
                    "CIS.No": "4.1",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                    "Host": host.name,
                    "Value": None,
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Syslog.global.logDir", host.name)
        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.1",
                "Name": "Persistent Syslog Configuration (Read Only)",
                "CIS.No": "5.1",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                "Host": host.name,
                "Value": None,
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Syslog.global.logDir 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "3.1",
                "Name": "Persistent Syslog Configuration (Read Only)",
                "CIS.No": "4.1",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                "Host": host.name,
                "Value": None,
                "Description": "Error retrieving syslog configuration",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Syslog.global.logDir 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        syslog_info = get_hosts_syslog_persistent(content)
        export_to_json(syslog_info, "../log/no_3.1_syslog_persistent.json")


if __name__ == "__main__":
    main()
