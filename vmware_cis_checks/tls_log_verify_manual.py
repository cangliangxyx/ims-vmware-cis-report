import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_tls_log_verify(content) -> List[Dict[str, Any]]:
    """检查是否启用了远程日志 TLS 证书验证（只读）"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logCheckCerts")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "3.5",
                    "Name": "Remote Syslog TLS certificate verification (Read Only)",
                    "CIS.No": "4.10",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logCheckCerts',
                    "Host": host.name,
                    "Value": setting.value,
                    "Description": "TLS certificate verification for remote logging",
                    "Error": None
                })
                logger.info("主机: %s, Syslog.global.logCheckCerts = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "3.5",
                    "Name": "Remote Syslog TLS certificate verification (Read Only)",
                    "CIS.No": "4.10",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logCheckCerts',
                    "Host": host.name,
                    "Value": None,
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Syslog.global.logCheckCerts", host.name)
        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.5",
                "Name": "Remote Syslog TLS certificate verification (Read Only)",
                "CIS.No": "4.10",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logCheckCerts',
                "Host": host.name,
                "Value": None,
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Syslog.global.logCheckCerts 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "3.5",
                "Name": "Remote Syslog TLS certificate verification (Read Only)",
                "CIS.No": "4.5",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logCheckCerts',
                "Host": host.name,
                "Value": None,
                "Description": "Error retrieving TLS log verification setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Syslog.global.logCheckCerts 失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        tls_log_info = get_hosts_tls_log_verify(content)
        export_to_json(tls_log_info, "../log/no_3.5_tls_log_verify_manual.json")


if __name__ == "__main__":
    main()
