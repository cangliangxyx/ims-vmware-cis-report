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


def get_hosts_mem_share_salt(content) -> List[Dict[str, Any]]:
    """获取每台主机的 Mem.ShareForceSalting 高级设置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Mem.ShareForceSalting")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "host": host.name,
                    "NO": "1.4",
                    "name": "Host must restrict inter-VM transparent page sharing (Automated)",
                    "CIS.NO": "2.10",
                    "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description',
                    "value": setting.value,
                    "type": type(setting.value).__name__,
                    "description": "Memory page sharing salt",
                })
                logger.info("主机: %s, %s = %s", host.name, setting.key, setting.value)
            else:
                results.append({
                    "host": host.name,
                    "NO": "1.4",
                    "name": "Host must restrict inter-VM transparent page sharing (Automated)",
                    "CIS.NO": "2.10",
                    "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description',
                    "value": None,
                    "type": None,
                    "description": "Not configured"
                })
                logger.warning("主机 %s 没有 Mem.ShareForceSalting 设置", host.name)

        except Exception as e:
            results.append({
                "host": host.name,
                "NO": "1.4",
                "name": "Host must restrict inter-VM transparent page sharing (Automated)",
                "CIS.NO": "2.10",
                "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description',
                "value": None,
                "error": str(e)
            })
            logger.error("主机 %s 获取 Mem.ShareForceSalting 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        mem_salt_info = get_hosts_mem_share_salt(content)
        export_to_json(mem_salt_info, "../log/no_1.4_mem_share_salt.json")


if __name__ == "__main__":
    main()
