# vmware_cis_checks tsm_ssh.py

import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)

def get_hosts_ssh_service(content) -> List[Dict[str, Any]]:
    """获取每台主机的 TSM-SSH 服务状态"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            service = next((s for s in host.configManager.serviceSystem.serviceInfo.service if s.key == "TSM-SSH"), None)
            if service:
                results.append({
                    "host": host.name,
                    "key": service.key,
                    "label": service.label,
                    "policy": service.policy,
                    "running": service.running,
                    "required": service.required
                })
            else:
                results.append({
                    "host": host.name,
                    "key": "TSM-SSH",
                    "error": "Service not found"
                })
        except Exception as e:
            results.append({
                "host": host.name,
                "key": "TSM-SSH",
                "error": str(e)
            })
    container.Destroy()
    return results

def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        ssh_info = get_hosts_ssh_service(content)
    export_to_json(ssh_info, "../log/2.1_ssh_service.json")

if __name__ == "__main__":
    main()
