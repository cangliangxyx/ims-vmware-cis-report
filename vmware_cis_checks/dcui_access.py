import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_dcui_access(content) -> List[Dict[str, Any]]:
    """查看每台主机的 DCUI.Access 用户列表（只读，不修改）"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("DCUI.Access")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "2.14",
                    "Name": "DCUI Access Users (Read Only)",
                    "CIS.No": "3.18",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name DCUI.Access',
                    "Host": host.name,
                    "Value": setting.value,
                    "Description": "DCUI access user list",
                    "Error": None
                })
                logger.info("主机: %s, DCUI.Access = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.14",
                    "Name": "DCUI Access Users (Read Only)",
                    "CIS.No": "3.18",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name DCUI.Access',
                    "Host": host.name,
                    "Value": None,
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 DCUI.Access", host.name)
        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "2.14",
                "Name": "DCUI Access Users (Read Only)",
                "CIS.No": "3.18",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name DCUI.Access',
                "Host": host.name,
                "Value": None,
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 DCUI.Access 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.14",
                "Name": "DCUI Access Users (Read Only)",
                "CIS.No": "3.18",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name DCUI.Access',
                "Host": host.name,
                "Value": None,
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 DCUI.Access 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        dcui_info = get_hosts_dcui_access(content)
        export_to_json(dcui_info, "../log/no_2.14_dcui_access.json")


if __name__ == "__main__":
    main()
