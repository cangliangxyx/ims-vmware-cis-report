import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_tls_version(content) -> List[Dict[str, Any]]:
    """查看每台主机的 TLS 协议配置（只读）"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            # VMware ESXi TLS 设置通常通过 UserVars.ESXiVPsTLSConfig 控制
            adv_settings = host.configManager.advancedOption.QueryOptions("UserVars.ESXiVPsTLSConfig")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "2.16",
                    "Name": "TLS Version Configuration (Read Only)",
                    "CIS.No": "3.21",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.ESXiVPsTLSConfig',
                    "Host": host.name,
                    "Value": setting.value,
                    "Description": "TLS protocol configuration",
                    "Error": None
                })
                logger.info("主机: %s, TLS Config = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.16",
                    "Name": "TLS Version Configuration (Read Only)",
                    "CIS.No": "3.21",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.ESXiVPsTLSConfig',
                    "Host": host.name,
                    "Value": None,
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 TLS 设置", host.name)
        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "2.16",
                "Name": "TLS Version Configuration (Read Only)",
                "CIS.No": "3.21",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.ESXiVPsTLSConfig',
                "Host": host.name,
                "Value": None,
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 TLS 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.16",
                "Name": "TLS Version Configuration (Read Only)",
                "CIS.No": "3.21",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.ESXiVPsTLSConfig',
                "Host": host.name,
                "Value": None,
                "Description": "Error retrieving TLS configuration",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 TLS 设置失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        tls_info = get_hosts_tls_version(content)
        export_to_json(tls_info, "../log/no_2.16_tls_version_manual.json")


if __name__ == "__main__":
    main()
