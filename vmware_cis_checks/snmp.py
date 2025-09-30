import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_snmp_service_info(content) -> List[Dict[str, Any]]:
    """
    收集每台主机的 SNMP 服务状态
    推荐值：停止
    :param content: vSphere service instance content
    :return: 每台主机 SNMP 服务检查结果列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    results: List[Dict[str, Any]] = []

    for host in container.view:
        record = {
            "AIIB.No": "2.4",
            "Name": "Host should deactivate SNMP",
            "CIS.No": "3.6",
            "CMD": "Get-VMHostService | Where {$_.Key -eq 'snmpd'}",
            "Host": host.name,
            "Value": None,
            "Status": "Fail",
            "Description": "SNMP 服务状态未检查",
            "Error": None
        }

        try:
            services = host.configManager.serviceSystem.serviceInfo.service
            snmp_service = next((s for s in services if s.key.lower() == "snmpd"), None)

            if snmp_service:
                status = "Pass" if not snmp_service.running else "Fail"
                record.update({
                    "Value": {
                        "key": snmp_service.key,
                        "label": snmp_service.label,
                        "running": snmp_service.running,
                        "required": snmp_service.required
                    },
                    "Status": status,
                    "Description": "snmp_service.running = True → 'running'; snmp_service.running = False → 'stopped'; 检测方法：'running': false"
                })
                logger.info("[SNMP] 主机: %s, SNMP运行: %s, Status: %s", host.name, snmp_service.running, status)
            else:
                record.update({
                    "Value": None,
                    "Status": "Fail",
                    "Description": "snmp_service.running = True → 'running'; snmp_service.running = False → 'stopped'; 检测方法：'running': false"
                })
                logger.warning("[SNMP] 主机 %s 未找到 SNMP 服务", host.name)

        except Exception as e:
            record.update({
                "Value": None,
                "Status": "Fail",
                "Description": "查询 SNMP 服务失败",
                "Error": str(e)
            })
            logger.error("[SNMP] 主机 %s 查询 SNMP 服务失败: %s", host.name, e)

        results.append(record)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机 SNMP 服务状态，输出为 JSON 文件
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_2.4_snmp_status.json")

    vsphere_data = settings.get_vsphere_config(os.getenv("project_env", "prod"))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_snmp_service_info(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[SNMP] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[SNMP] 所有主机 SNMP 服务检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
