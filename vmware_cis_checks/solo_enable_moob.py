# vmware_cis_checks/solo_enable_moob.py

import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)

def get_hosts_solo_enable_mob(content) -> List[Dict[str, Any]]:
    """获取每台主机的 Config.HostAgent.plugins.solo.enableMob 高级设置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Config.HostAgent.plugins.solo.enableMob")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "host": host.name,
                    "name": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__,
                    "description": "Enable direct MOB access"  # 手动添加描述
                })
            else:
                results.append({
                    "host": host.name,
                    "name": "Config.HostAgent.plugins.solo.enableMob",
                    "value": None,
                    "type": None,
                    "description": "Not configured"
                })
        except Exception as e:
            results.append({
                "host": host.name,
                "name": "Config.HostAgent.plugins.solo.enableMob",
                "value": None,
                "error": str(e)
            })
    container.Destroy()
    return results

def main():
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        solo_info = get_hosts_solo_enable_mob(content)
    export_to_json(solo_info, "../log/2.3_solo_enable_mob.json")

if __name__ == "__main__":
    main()
