import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_account_lock_failure(content) -> List[Dict[str, Any]]:
    """
    通过 vSphere SDK 获取每台主机的 Security.AccountLockFailures 配置
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Security.AccountLockFailures")
            if adv_settings:
                setting = adv_settings[0]
                raw_value = {
                    "key": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__
                }
                results.append({
                    "AIIB.No": "2.8",
                    "Name": "Host must lock an account after a specified number of failed login attempts",
                    "CIS.No": "3.12",
                    "CMD": "host->configure->advanced system setting->Security.AccountLockFailures",
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": """检测值:控制登录失败后锁定账户的次数。检测方法："value": 5""",
                    "Error": None
                })
                logger.info("主机 %s Security.AccountLockFailures 原始值: %s", host.name, raw_value)
            else:
                results.append({
                    "AIIB.No": "2.8",
                    "Name": "Host must lock an account after a specified number of failed login attempts",
                    "CIS.No": "3.12",
                    "CMD": "Get-AdvancedSetting -Name Security.AccountLockFailures",
                    "Host": host.name,
                    "Value": None,
                    "Description": "未找到 Security.AccountLockFailures 设置，表示未配置账号锁定策略",
                    "Error": None
                })
                logger.warning("主机 %s 未找到 Security.AccountLockFailures 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "2.8",
                "Name": "Host must lock an account after a specified number of failed login attempts",
                "CIS.No": "3.12",
                "CMD": "Get-AdvancedSetting -Name Security.AccountLockFailures",
                "Host": host.name,
                "Value": None,
                "Description": "查询 Security.AccountLockFailures 失败",
                "Error": str(e)
            })
            logger.error("主机 %s 查询 Security.AccountLockFailures 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    使用 VsphereConnection 获取 Security.AccountLockFailures 原始值并导出 JSON
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_2.8_account_lock_failure.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        account_lock_info = get_hosts_account_lock_failure(content)
        export_to_json(account_lock_info, output_path)
        logger.info("Security.AccountLockFailures 原始值检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
