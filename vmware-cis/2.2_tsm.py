# vmware-cis/2.2_tsm.py

import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)

def get_hosts_tsm_service(content) -> List[Dict[str, Any]]:
    """获取每台主机的 TSM 服务状态"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            service = next((s for s in host.configManager.serviceSystem.serviceInfo.service if s.key == "TSM"), None)
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
                    "key": "TSM",
                    "error": "Service not found"
                })
        except Exception as e:
            results.append({
                "host": host.name,
                "key": "TSM",
                "error": str(e)
            })
    container.Destroy()
    return results

def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        tsm_info = get_hosts_tsm_service(content)
    export_to_json(tsm_info, "../log/2.2_tsm_service.json")

if __name__ == "__main__":
    main()

