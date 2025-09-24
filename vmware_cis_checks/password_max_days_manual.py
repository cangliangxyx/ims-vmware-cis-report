import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_password_max_days(content) -> List[Dict[str, Any]]:
    """获取每台主机的 Security.PasswordMaxDays 设置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Security.PasswordMaxDays")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "2.11",
                    "Name": "Host must enforce maximum password age (Automated)",
                    "CIS.No": "3.15",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordMaxDays',
                    "Host": host.name,
                    "Value": {
                        "key": setting.key,
                        "value": setting.value,
                        "type": type(setting.value).__name__
                    },
                    "Description": "Maximum password age (days)",
                    "Error": None
                })
                logger.info("主机: %s, Security.PasswordMaxDays = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.11",
                    "Name": "Host must enforce maximum password age (Automated)",
                    "CIS.No": "3.15",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordMaxDays',
                    "Host": host.name,
                    "Value": {"key": "Security.PasswordMaxDays", "value": None, "type": None},
                    "Description": "Not configured or not supported on this host",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Security.PasswordMaxDays 或不支持该设置", host.name)
        except vim.fault.InvalidName as e:
            # 特殊处理 InvalidName，不当作报错
            results.append({
                "AIIB.No": "2.11",
                "Name": "Host must enforce maximum password age (Automated)",
                "CIS.No": "3.15",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordMaxDays',
                "Host": host.name,
                "Value": {"key": "Security.PasswordMaxDays", "value": None, "type": None},
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Security.PasswordMaxDays 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.11",
                "Name": "Host must enforce maximum password age (Automated)",
                "CIS.No": "3.15",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordMaxDays',
                "Host": host.name,
                "Value": {"key": "Security.PasswordMaxDays", "value": None, "type": None},
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Security.PasswordMaxDays 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        max_days_info = get_hosts_password_max_days(content)
        export_to_json(max_days_info, "../log/no_2.11_password_max_days_manual.json")


if __name__ == "__main__":
    main()
