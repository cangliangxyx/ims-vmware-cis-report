import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_idle_host_client_timeout(content) -> List[Dict[str, Any]]:
    """查看每台主机的 Host Client idle 超时配置（只读，不修改）"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("UserVars.HostClientSessionTimeout")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "2.13",
                    "Name": "Host Client idle session timeout (Read Only)",
                    "CIS.No": "3.17",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.HostClientSessionTimeout',
                    "Host": host.name,
                    "Value": setting.value,
                    "Description": "Idle host client session timeout (seconds)",
                    "Error": None
                })
                logger.info("主机: %s, HostClientSessionTimeout = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.13",
                    "Name": "Host Client idle session timeout (Read Only)",
                    "CIS.No": "3.17",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.HostClientSessionTimeout',
                    "Host": host.name,
                    "Value": None,
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 HostClientSessionTimeout", host.name)
        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "2.13",
                "Name": "Host Client idle session timeout (Read Only)",
                "CIS.No": "3.17",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.HostClientSessionTimeout',
                "Host": host.name,
                "Value": None,
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 UserVars.HostClientSessionTimeout 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.13",
                "Name": "Host Client idle session timeout (Read Only)",
                "CIS.No": "3.17",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.HostClientSessionTimeout',
                "Host": host.name,
                "Value": None,
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 HostClientSessionTimeout 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        timeout_info = get_hosts_idle_host_client_timeout(content)
        export_to_json(timeout_info, "../log/no_2.13_idle_host_client_manual.json")


if __name__ == "__main__":
    main()
