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

def get_hosts_dcui_timeout(content) -> List[Dict[str, Any]]:
    """获取每台主机的 UserVars.DcuiTimeOut 设置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("UserVars.DcuiTimeOut")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "2.5",
                    "Name": "Host must automatically terminate idle DCUI sessions (Automated)",
                    "CIS.No": "3.7",
                    "CMD": r"Get-VMHost | Get-AdvancedSetting -Name UserVars.DcuiTimeOut",
                    "Host": host.name,
                    "Value": {
                        "key": setting.key,
                        "value": setting.value,
                        "type": type(setting.value).__name__
                    },
                    "Description": "DCUI idle timeout in seconds",
                    "Error": None
                })
                logger.info("主机: %s, UserVars.DcuiTimeOut = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.5",
                    "Name": "Host must automatically terminate idle DCUI sessions (Automated)",
                    "CIS.No": "3.7",
                    "CMD": r"Get-VMHost | Get-AdvancedSetting -Name UserVars.DcuiTimeOut",
                    "Host": host.name,
                    "Value": {"key": "UserVars.DcuiTimeOut", "value": None, "type": None},
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 没有配置 UserVars.DcuiTimeOut", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.5",
                "Name": "Host must automatically terminate idle DCUI sessions (Automated)",
                "CIS.No": "3.7",
                "CMD": r"Get-VMHost | Get-AdvancedSetting -Name UserVars.DcuiTimeOut",
                "Host": host.name,
                "Value": {"key": "UserVars.DcuiTimeOut", "value": None, "type": None},
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 UserVars.DcuiTimeOut 失败: %s", host.name, e)

    container.Destroy()
    return results

def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        dcui_info = get_hosts_dcui_timeout(content)
        export_to_json(dcui_info, "../log/no_2.5_dcui_timeout.json")

if __name__ == "__main__":
    main()
