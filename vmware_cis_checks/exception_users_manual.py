import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_exception_users(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的 Lockdown Mode Exception Users 配置（只读，不修改）
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Config.HostAgent.plugins.hostsvc.esxAdminsGroup")
            if adv_settings:
                setting = adv_settings[0]
                raw_value = {
                    "key": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__
                }
                results.append({
                    "AIIB.No": "2.15",
                    "Name": "Lockdown Mode Exception Users (Read Only)",
                    "CIS.No": "3.19",
                    "CMD": "host->configure->security profile->lockdown mode->exception users",
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": """Lockdown Mode 的例外用户组，通常为 'ESX Admins'。
如果为空字符串表示未配置例外用户。
建议：仅配置必要的例外用户组，降低风险。""",
                    "Error": None
                })
                logger.info("主机 %s Exception Users 原始值: %s", host.name, raw_value)
            else:
                results.append({
                    "AIIB.No": "2.15",
                    "Name": "Lockdown Mode Exception Users (Read Only)",
                    "CIS.No": "3.19",
                    "CMD": "host->configure->security profile->lockdown mode->exception users",
                    "Host": host.name,
                    "Value": {"key": "Config.HostAgent.plugins.hostsvc.esxAdminsGroup", "value": None, "type": None},
                    "Description": "未配置任何例外用户组，Lockdown Mode 下无人可直接登录",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Exception Users", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "2.15",
                "Name": "Lockdown Mode Exception Users (Read Only)",
                "CIS.No": "3.19",
                "CMD": "Get-AdvancedSetting -Name Config.HostAgent.plugins.hostsvc.esxAdminsGroup",
                "Host": host.name,
                "Value": None,
                "Description": "此主机不支持 Lockdown Mode Exception Users 设置",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 ExceptionUsers 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "2.15",
                "Name": "Lockdown Mode Exception Users (Read Only)",
                "CIS.No": "3.19",
                "CMD": "Get-AdvancedSetting -Name Config.HostAgent.plugins.hostsvc.esxAdminsGroup",
                "Host": host.name,
                "Value": None,
                "Description": "查询 Exception Users 配置失败",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 ExceptionUsers 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查主机 Lockdown Mode Exception Users 并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_2.15_exception_users.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        exc_users_info = get_hosts_exception_users(content)
        export_to_json(exc_users_info, output_path)
        logger.info("Lockdown Mode Exception Users 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
