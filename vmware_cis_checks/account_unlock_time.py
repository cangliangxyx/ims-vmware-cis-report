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


def get_hosts_account_unlock_time(content) -> List[Dict[str, Any]]:
    """检查每台主机 Security.AccountUnlockTime 设置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Security.AccountUnlockTime")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "host": host.name,
                    "NO": "2.9",
                    "name": "Host must unlock accounts after a specified timeout period (Automated)",
                    "CIS.NO": "3.13",
                    "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime',
                    "value": setting.value,
                    "type": type(setting.value).__name__,
                    "description": "Timeout period after which locked account is unlocked (seconds)"
                })
                logger.info("主机: %s, Security.AccountUnlockTime = %s", host.name, setting.value)
            else:
                results.append({
                    "host": host.name,
                    "NO": "2.9",
                    "name": "Host must unlock accounts after a specified timeout period (Automated)",
                    "CIS.NO": "3.13",
                    "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime',
                    "value": None,
                    "type": None,
                    "description": "Not configured"
                })
                logger.warning("主机 %s 没有配置 Security.AccountUnlockTime", host.name)
        except Exception as e:
            results.append({
                "host": host.name,
                "NO": "2.9",
                "name": "Host must unlock accounts after a specified timeout period (Automated)",
                "CIS.NO": "3.13",
                "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime',
                "value": None,
                "error": str(e)
            })
            logger.error("主机 %s 获取 Security.AccountUnlockTime 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        info = get_hosts_account_unlock_time(content)
        export_to_json(info, "../log/no_2.9_account_unlock_time.json")


if __name__ == "__main__":
    main()
