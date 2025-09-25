import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_password_history(content) -> List[Dict[str, Any]]:
    """获取每台主机的 Security.PasswordHistory 设置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Security.PasswordHistory")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "2.10",
                    "Name": "Host must enforce password history (Automated)",
                    "CIS.No": "3.14",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordHistory',
                    "Host": host.name,
                    "Value": {
                        "key": setting.key,
                        "value": setting.value,
                        "type": type(setting.value).__name__
                    },
                    "Description": "Password history count",
                    "Error": None
                })
                logger.info("主机: %s, Security.PasswordHistory = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.10",
                    "Name": "Host must enforce password history (Automated)",
                    "CIS.No": "3.14",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordHistory',
                    "Host": host.name,
                    "Value": {"key": "Security.PasswordHistory", "value": None, "type": None},
                    "Description": "Not configured or not supported on this host",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Security.PasswordHistory 或不支持此设置", host.name)
        except vim.fault.InvalidName as e:
            # 特殊处理 InvalidName，不当作报错
            results.append({
                "AIIB.No": "2.10",
                "Name": "Host must enforce password history (Automated)",
                "CIS.No": "3.14",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordHistory',
                "Host": host.name,
                "Value": {"key": "Security.PasswordHistory", "value": None, "type": None},
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Security.PasswordHistory 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.10",
                "Name": "Host must enforce password history (Automated)",
                "CIS.No": "3.14",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordHistory',
                "Host": host.name,
                "Value": {"key": "Security.PasswordHistory", "value": None, "type": None},
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Security.PasswordHistory 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查主机密码历史策略并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_2.10_password_history_manual.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        history_info = get_hosts_password_history(content)
        export_to_json(history_info, output_path)



if __name__ == "__main__":
    main()
