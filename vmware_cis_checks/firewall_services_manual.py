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


def get_hosts_firewall_services(content) -> List[Dict[str, Any]]:
    """获取每台主机的防火墙服务配置 (手工检查是否限制为授权网段)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            fw_system = host.configManager.firewallSystem
            rules = fw_system.firewallInfo.ruleset

            services = []
            for r in rules:
                allowed = []
                if r.allowedHosts:
                    if r.allowedHosts.allIp:
                        allowed = ["All"]
                    elif r.allowedHosts.ipAddress:
                        allowed = list(r.allowedHosts.ipAddress)

                services.append({
                    "name": r.key,
                    "enabled": r.enabled,
                    "allowed_hosts": allowed
                })

            results.append({
                "AIIB.No": "4.1",
                "Name": "Host firewall services must be restricted to authorized networks (Manual)",
                "CIS.No": "5.1",
                "CMD": r'Get-VMHost | Get-VMHostFirewallException | Select-Object Name, Enabled, AllowedHosts',
                "Host": host.name,
                "Value": services,
                "Description": "Firewall services and allowed networks",
                "Error": None
            })
            logger.info("主机 %s 防火墙规则数: %s", host.name, len(services))

        except Exception as e:
            results.append({
                "AIIB.No": "4.1",
                "Name": "Host firewall services must be restricted to authorized networks (Manual)",
                "CIS.No": "5.1",
                "CMD": r'Get-VMHost | Get-VMHostFirewallException | Select-Object Name, Enabled, AllowedHosts',
                "Host": host.name,
                "Value": [],
                "Description": "Firewall services retrieval error",
                "Error": str(e)
            })
            logger.error("主机 %s 获取防火墙服务失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_4.1_firewall_services_manual.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        fw_info = get_hosts_firewall_services(content)
        export_to_json(fw_info, output_path)


if __name__ == "__main__":
    main()
