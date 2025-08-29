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


def get_hosts_account_lock_failure(content) -> List[Dict[str, Any]]:
    """检查每台主机 Security.AccountLockFailure 设置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Security.AccountLockFailure")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "host": host.name,
                    "NO": "2.8",
                    "name": "Host must lock an account after a specified number of failed login attempts (Automated)",
                    "CIS.NO": "3.12",
                    "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountLockFailure',
                    "value": setting.value,
                    "type": type(setting.value).__name__,
                    "description": "Number of failed login attempts before lockout"
                })
                logger.info("主机: %s, Security.AccountLockFailure = %s", host.name, setting.value)
            else:
                results.append({
                    "host": host.name,
                    "NO": "2.8",
                    "name": "Host must lock an account after a specified number of failed login attempts (Automated)",
                    "CIS.NO": "3.12",
                    "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountLockFailure',
                    "value": None,
                    "type": None,
                    "description": "Not configured"
                })
                logger.warning("主机 %s 没有配置 Security.AccountLockFailure", host.name)
        except Exception as e:
            results.append({
                "host": host.name,
                "NO": "2.8",
                "name": "Host must lock an account after a specified number of failed login attempts (Automated)",
                "CIS.NO": "3.12",
                "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountLockFailure',
                "value": None,
                "error": str(e)
            })
            logger.error("主机 %s 获取 Security.AccountLockFailure 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        info = get_hosts_account_lock_failure(content)
        export_to_json(info, "../log/no_2.8_account_lock_failure.json")


if __name__ == "__main__":
    main()
