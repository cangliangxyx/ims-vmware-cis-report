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


def get_hosts_tsm_service(content) -> List[Dict[str, Any]]:
    """获取每台主机的 TSM 服务状态"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            service = next(
                (s for s in host.configManager.serviceSystem.serviceInfo.service if s.key == "TSM"),
                None
            )
            if service:
                results.append({
                    "host": host.name,
                    "NO": "2.2",
                    "name": "Host must deactivate the ESXi shell (Automated)",
                    "CIS.NO": "3.2",
                    "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM" } | Select Key, Label, Policy, Running, Required',
                    "key": service.key,
                    "label": service.label,
                    "policy": service.policy,
                    "running": service.running,
                    "required": service.required
                })
                logger.info("主机: %s, TSM 服务运行状态: %s, 策略: %s", host.name, service.running, service.policy)
            else:
                results.append({
                    "host": host.name,
                    "NO": "2.2",
                    "name": "Host must deactivate the ESXi shell (Automated)",
                    "CIS.NO": "3.2",
                    "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM" } | Select Key, Label, Policy, Running, Required',
                    "key": "TSM",
                    "error": "Service not found"
                })
                logger.warning("主机 %s 没有找到 TSM 服务", host.name)

        except Exception as e:
            results.append({
                "host": host.name,
                "NO": "2.2",
                "name": "Host must deactivate the ESXi shell (Automated)",
                "CIS.NO": "3.2",
                "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM" } | Select Key, Label, Policy, Running, Required',
                "key": "TSM",
                "error": str(e)
            })
            logger.error("主机 %s 获取 TSM 服务状态失败: %s", host.name, e)

    container.Destroy()
    return results


def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        tsm_info = get_hosts_tsm_service(content)
        export_to_json(tsm_info, "../log/no_2.2_tsm.json")


if __name__ == "__main__":
    main()
