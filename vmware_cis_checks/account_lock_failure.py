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
                    "AIIB.No": "2.8",
                    "Name": "Host must lock an account after a specified number of failed login attempts (Automated)",
                    "CIS.No": "3.12",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountLockFailure',
                    "Host": host.name,
                    "Value": {
                        "key": setting.key,
                        "value": setting.value,
                        "type": type(setting.value).__name__
                    },
                    "Description": "Number of failed login attempts before lockout",
                    "Error": None
                })
                logger.info("主机: %s, Security.AccountLockFailure = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.8",
                    "Name": "Host must lock an account after a specified number of failed login attempts (Automated)",
                    "CIS.No": "3.12",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountLockFailure',
                    "Host": host.name,
                    "Value": {"key": "Security.AccountLockFailure", "value": None, "type": None},
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 没有配置 Security.AccountLockFailure", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.8",
                "Name": "Host must lock an account after a specified number of failed login attempts (Automated)",
                "CIS.No": "3.12",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountLockFailure',
                "Host": host.name,
                "Value": {"key": "Security.AccountLockFailure", "value": None, "type": None},
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Security.AccountLockFailure 失败: %s", host.name, e)

    container.Destroy()
    return results

def main(output_dir: str = None):
    """
    检查主机账号锁定失败策略并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_2.8_account_lock_failure.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        info = get_hosts_account_lock_failure(content)
        export_to_json(info, output_path)


if __name__ == "__main__":
    main()
