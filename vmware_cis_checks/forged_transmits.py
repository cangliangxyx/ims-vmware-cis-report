import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_forged_transmits(content) -> List[Dict[str, Any]]:
    """检查标准 vSwitch 是否拒绝 Forged Transmits"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            vswitches = host.config.network.vswitch
            for vs in vswitches:
                policy = vs.spec.policy.security
                results.append({
                    "AIIB.No": "4.4",
                    "Name": "Host standard vSwitch must reject Forged Transmits",
                    "CIS.No": "5.6",
                    "CMD": r'Get-VirtualSwitch | Select Name, @{Name="ForgedTransmits";Expression={$_.Policy.Security.ForgedTransmits}}',
                    "Host": host.name,
                    "Value": {
                        "vswitch": vs.name,
                        "mac_changes": "Accept" if policy.macChanges else "Reject",
                        "promiscuous_mode": "Accept" if policy.allowPromiscuous else "Reject",
                        "forged_transmits": "Accept" if policy.forgedTransmits else "Reject"
                    },
                    "Description": "vSwitch security policies for Forged Transmits, MAC changes, and Promiscuous mode",
                    "Error": None
                })
                logger.info("主机 %s vSwitch %s ForgedTransmits=%s", host.name, vs.name, policy.forgedTransmits)
        except Exception as e:
            results.append({
                "AIIB.No": "4.4",
                "Name": "Host standard vSwitch must reject Forged Transmits",
                "CIS.No": "5.6",
                "CMD": r'Get-VirtualSwitch | Select Name, @{Name="ForgedTransmits";Expression={$_.Policy.Security.ForgedTransmits}}',
                "Host": host.name,
                "Value": None,
                "Description": "vSwitch security policies retrieval error",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 vSwitch 安全策略失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查所有主机标准 vSwitch Forged Transmits 设置并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_4.4_forged_transmits.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        forged_info = get_hosts_forged_transmits(content)
        export_to_json(forged_info, output_path)


if __name__ == "__main__":
    main()
