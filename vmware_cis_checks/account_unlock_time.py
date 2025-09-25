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
                    "AIIB.No": "2.9",
                    "Name": "Host must unlock accounts after a specified timeout period (Automated)",
                    "CIS.No": "3.13",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime',
                    "Host": host.name,
                    "Value": {
                        "key": setting.key,
                        "value": setting.value,
                        "type": type(setting.value).__name__
                    },
                    "Description": "Timeout period after which locked account is unlocked (seconds)",
                    "Error": None
                })
                logger.info("主机: %s, Security.AccountUnlockTime = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.9",
                    "Name": "Host must unlock accounts after a specified timeout period (Automated)",
                    "CIS.No": "3.13",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime',
                    "Host": host.name,
                    "Value": {"key": "Security.AccountUnlockTime", "value": None, "type": None},
                    "Description": "Not configured or not supported on this host",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Security.AccountUnlockTime 或不支持此设置", host.name)
        except vim.fault.InvalidName as e:
            # 特殊处理 InvalidName，不当作报错
            results.append({
                "AIIB.No": "2.9",
                "Name": "Host must unlock accounts after a specified timeout period (Automated)",
                "CIS.No": "3.13",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime',
                "Host": host.name,
                "Value": {"key": "Security.AccountUnlockTime", "value": None, "type": None},
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Security.AccountUnlockTime 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.9",
                "Name": "Host must unlock accounts after a specified timeout period (Automated)",
                "CIS.No": "3.13",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime',
                "Host": host.name,
                "Value": {"key": "Security.AccountUnlockTime", "value": None, "type": None},
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Security.AccountUnlockTime 失败: %s", host.name, e)

    container.Destroy()
    return results

def main(output_dir: str = None):
    """
    检查主机账号解锁时间策略并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_2.9_account_unlock_time.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        info = get_hosts_account_unlock_time(content)
        export_to_json(info, output_path)

if __name__ == "__main__":
    main()
