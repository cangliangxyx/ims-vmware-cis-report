import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_snmp_status(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的 SNMP 服务原始状态信息
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            services = host.configManager.serviceSystem.serviceInfo.service
            snmp_service = next((s for s in services if s.key.lower() == "snmpd"), None)

            if snmp_service:
                # 直接输出原始属性
                raw_value = {
                    "key": snmp_service.key,
                    "label": snmp_service.label,
                    "running": snmp_service.running,
                    "required": snmp_service.required,
                }
                results.append({
                    "AIIB.No": "2.4",
                    "Name": "Host should deactivate SNMP",
                    "CIS.No": "3.6",
                    "CMD": "Get-VMHostService | Where {$_.Key -eq 'snmpd'}",
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": """
                    检测值: host-->configure->services --> snmp server 的值，
                    snmp_service.running = True → "status": "running"，
                    snmp_service.running = False → "status": "stopped"，
                    检测方法：Value -> running = False
                    """,
                    "Error": None
                })
                logger.info("主机 %s SNMP 原始值: %s", host.name, raw_value)
            else:
                results.append({
                    "AIIB.No": "2.4",
                    "Name": "Host should deactivate SNMP",
                    "CIS.No": "3.6",
                    "CMD": "Get-VMHostService | Where {$_.Key -eq 'snmpd'}",
                    "Host": host.name,
                    "Value": None,
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
    使用 VsphereConnection 获取 SNMP 服务原始值并导出 JSON
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_2.4_snmp_status.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        snmp_info = get_hosts_snmp_status(content)
        export_to_json(snmp_info, output_path)
        logger.info("SNMP 原始值检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
