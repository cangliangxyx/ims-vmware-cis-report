import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vss_security_policies(content) -> List[Dict[str, Any]]:
    """获取标准虚拟交换机的安全策略 (混杂模式、MAC 修改、伪造传输)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            network_system = host.configManager.networkSystem
            vss_list = network_system.networkConfig.vswitch or []

            vss_info = []
            for vss in vss_list:
                sec = vss.spec.policy.security
                vss_info.append({
                    "vswitch": vss.name,
                    "promiscuous_mode": "Accept" if sec.allowPromiscuous else "Reject",
                    "mac_changes": "Accept" if sec.macChanges else "Reject",
                    "forged_transmits": "Accept" if sec.forgedTransmits else "Reject",
                })

            results.append({
                "AIIB.No": "4.6",
                "Name": "Host standard vSwitch must reject Promiscuous Mode",
                "CIS.No": "5.8",
                "CMD": r'Get-VirtualSwitch | Select Name, @{Name="PromiscuousMode";Expression={$_.Policy.Security.AllowPromiscuous}}',
                "Host": host.name,
                "Value": vss_info,
                "Description": "Standard vSwitch security policies for Promiscuous mode, MAC changes, and Forged Transmits",
                "Error": None
            })
            logger.info("主机 %s vSwitch 数: %s", host.name, len(vss_info))

        except Exception as e:
            results.append({
                "AIIB.No": "4.6",
                "Name": "Host standard vSwitch must reject Promiscuous Mode",
                "CIS.No": "5.8",
                "CMD": r'Get-VirtualSwitch | Select Name, @{Name="PromiscuousMode";Expression={$_.Policy.Security.AllowPromiscuous}}',
                "Host": host.name,
                "Value": None,
                "Description": "Standard vSwitch security policies retrieval error",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 vSwitch 配置失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查所有主机标准 vSwitch Promiscuous Mode 设置并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_4.6_vss_promiscuous_mode.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vss_info = get_vss_security_policies(content)
        export_to_json(vss_info, output_path)


if __name__ == "__main__":
    main()
