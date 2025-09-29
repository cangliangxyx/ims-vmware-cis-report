import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_shell_warning_status(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的 UserVars.SuppressShellWarning 原始值
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("UserVars.SuppressShellWarning")
            if adv_settings:
                setting = adv_settings[0]
                raw_value = {
                    "key": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__
                }
                results.append({
                    "AIIB.No": "2.6",
                    "Name": "Host must not suppress warnings that the shell is enabled",
                    "CIS.No": "3.10",
                    "CMD": "host->configure->advanced system setting->UserVars.SuppressShellWarning",
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": """当 value=1 表示抑制警告，不符合要求；
当 value=0 表示显示警告，符合要求。
检测方法：应检查 "value" == 0""",
                    "Error": None
                })
                logger.info("主机 %s UserVars.SuppressShellWarning 原始值: %s", host.name, raw_value)
            else:
                results.append({
                    "AIIB.No": "2.6",
                    "Name": "Host must not suppress warnings that the shell is enabled",
                    "CIS.No": "3.10",
                    "CMD": "Get-VMHost | Get-AdvancedSetting -Name UserVars.SuppressShellWarning",
                    "Host": host.name,
                    "Value": None,
                    "Description": "未找到 UserVars.SuppressShellWarning 高级设置",
                    "Error": None
                })
                logger.warning("主机 %s 未找到 UserVars.SuppressShellWarning 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "2.6",
                "Name": "Host must not suppress warnings that the shell is enabled",
                "CIS.No": "3.10",
                "CMD": "Get-VMHost | Get-AdvancedSetting -Name UserVars.SuppressShellWarning",
                "Host": host.name,
                "Value": None,
                "Description": "查询 UserVars.SuppressShellWarning 失败",
                "Error": str(e)
            })
            logger.error("主机 %s 查询 UserVars.SuppressShellWarning 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    使用 VsphereConnection 获取 UserVars.SuppressShellWarning 原始值并导出 JSON
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_2.6_shell_warning_status.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        shell_warning_info = get_hosts_shell_warning_status(content)
        export_to_json(shell_warning_info, output_path)
        logger.info("UserVars.SuppressShellWarning 原始值检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
