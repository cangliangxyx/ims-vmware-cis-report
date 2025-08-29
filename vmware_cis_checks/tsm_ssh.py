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


def get_hosts_ssh_service(content) -> List[Dict[str, Any]]:
    """获取每台主机的 TSM-SSH 服务状态"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            service = next(
                (s for s in host.configManager.serviceSystem.serviceInfo.service if s.key == "TSM-SSH"),
                None
            )
            if service:
                results.append({
                    "host": host.name,
                    "NO": "2.1",
                    "name": "Host should deactivate SSH (Automated)",
                    "CIS.NO": "3.1",
                    "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select Key, Label, Policy, Running, Required',
                    "key": service.key,
                    "label": service.label,
                    "policy": service.policy,
                    "running": service.running,
                    "required": service.required
                })
                logger.info("主机: %s, SSH 服务运行状态: %s, 策略: %s", host.name, service.running, service.policy)
            else:
                results.append({
                    "host": host.name,
                    "NO": "2.1",
                    "name": "Host should deactivate SSH (Automated)",
                    "CIS.NO": "3.1",
                    "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select Key, Label, Policy, Running, Required',
                    "key": "TSM-SSH",
                    "error": "Service not found"
                })
                logger.warning("主机 %s 没有找到 TSM-SSH 服务", host.name)

        except Exception as e:
            results.append({
                "host": host.name,
                "NO": "2.1",
                "name": "Host should deactivate SSH (Automated)",
                "CIS.NO": "3.1",
                "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select Key, Label, Policy, Running, Required',
                "key": "TSM-SSH",
                "error": str(e)
            })
            logger.error("主机 %s 获取 SSH 服务状态失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        ssh_info = get_hosts_ssh_service(content)
        export_to_json(ssh_info, "../log/no_2.1_tsm_ssh.json")


if __name__ == "__main__":
    main()
