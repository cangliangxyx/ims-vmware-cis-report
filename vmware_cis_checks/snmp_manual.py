import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_snmp_status(content) -> List[Dict[str, Any]]:
    """
    通过 vSphere SDK 获取每台主机的 SNMP 服务状态
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            services = host.configManager.serviceSystem.serviceInfo.service
            snmp_service = next((s for s in services if s.key.lower() == "snmpd"), None)

            if snmp_service:
                value = "enabled" if snmp_service.running else "disabled"
                results.append({
                    "AIIB.No": "2.4",
                    "Name": "Host should deactivate SNMP",
                    "CIS.No": "3.6",
                    "CMD": "Get-VMHostService | Where {$_.Key -eq 'snmpd'}",
                    "Host": host.name,
                    "Value": value,
                    "Description": "SNMP 服务当前状态",
                    "Error": None
                })
                logger.info("主机: %s, SNMP 状态: %s", host.name, value)
            else:
                results.append({
                    "AIIB.No": "2.4",
                    "Name": "Host should deactivate SNMP",
                    "CIS.No": "3.6",
                    "CMD": "Get-VMHostService | Where {$_.Key -eq 'snmpd'}",
                    "Host": host.name,
                    "Value": "not_found",
                    "Description": "此主机未找到 SNMP 服务条目",
                    "Error": None
                })
                logger.warning("主机 %s 未找到 SNMP 服务", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "2.4",
                "Name": "Host should deactivate SNMP",
                "CIS.No": "3.6",
                "CMD": "Get-VMHostService | Where {$_.Key -eq 'snmpd'}",
                "Host": host.name,
                "Value": None,
                "Description": "查询 SNMP 状态失败",
                "Error": str(e)
            })
            logger.error("主机 %s 查询 SNMP 服务失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    连接 vCenter 并导出每台主机 SNMP 服务状态
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_2.4_snmp_status.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        snmp_info = get_hosts_snmp_status(content)
        export_to_json(snmp_info, output_path)
        logger.info("SNMP 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
