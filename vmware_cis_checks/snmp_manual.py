import logging
from typing import List, Dict, Any
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_snmp_status(si) -> List[Dict[str, Any]]:
    """
    通过 vSphere SDK 获取每台主机的 SNMP 服务状态
    """
    content = si.RetrieveContent()
    results = []

    for datacenter in content.rootFolder.childEntity:
        host_folder = datacenter.hostFolder
        for compute_resource in host_folder.childEntity:
            for host in compute_resource.host:
                try:
                    services = host.configManager.serviceSystem.serviceInfo.service
                    snmp_service = next((s for s in services if s.key.lower() == "snmpd"), None)

                    if snmp_service:
                        value = "enabled" if snmp_service.running else "disabled"
                        results.append({
                            "AIIB.No": "2.4",
                            "Name": "Host should deactivate SNMP",
                            "CIS.No": "3.6",
                            "CMD": "自动检查: 获取 SNMP 服务状态",
                            "Host": host.name,
                            "Value": value,
                            "Description": "SNMP 服务当前状态",
                            "Error": None
                        })
                        logger.info(f"[{host.name}] SNMP 状态: {value}")
                    else:
                        results.append({
                            "AIIB.No": "2.4",
                            "Name": "Host should deactivate SNMP",
                            "CIS.No": "3.6",
                            "CMD": "自动检查: 获取 SNMP 服务状态",
                            "Host": host.name,
                            "Value": "not_found",
                            "Description": "此主机未找到 SNMP 服务条目",
                            "Error": None
                        })
                        logger.warning(f"[{host.name}] 未找到 SNMP 服务")
                except Exception as e:
                    results.append({
                        "AIIB.No": "2.4",
                        "Name": "Host should deactivate SNMP",
                        "CIS.No": "3.6",
                        "CMD": "自动检查: 获取 SNMP 服务状态",
                        "Host": host.name,
                        "Value": None,
                        "Description": "查询 SNMP 状态失败",
                        "Error": str(e)
                    })
                    logger.error(f"[{host.name}] 查询 SNMP 服务失败: {e}")

    return results


def main(vcenter: str, user: str, password: str, output_dir: str = None):
    """
    连接 vCenter 并导出每台主机 SNMP 服务状态
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_2.4_snmp_status.json"

    # 忽略 SSL 证书警告（实验/内网环境常用）
    context = ssl._create_unverified_context()
    si = SmartConnect(host=vcenter, user=user, pwd=password, sslContext=context)

    try:
        snmp_info = get_hosts_snmp_status(si)
        export_to_json(snmp_info, output_path)
        logger.info(f"SNMP 检查结果已导出到 {output_path}")
    finally:
        Disconnect(si)


if __name__ == "__main__":
    main(vcenter="your-vcenter.local", user="administrator@vsphere.local", password="yourpassword")
