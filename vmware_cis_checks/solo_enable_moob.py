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
                    "AIIB.No": "2.3",
                    "Name": "Host must restrict direct MOB access",
                    "CIS.No": "3.3",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Config.HostAgent.plugins.solo.enableMob | Select Name, Value, Type, Description',
                    "Host": host.name,
                    "Value": {
                        "key": setting.key,
                        "value": setting.value,
                        "type": type(setting.value).__name__
                    },
                    "Description": "Enable direct MOB access",
                    "Error": None
                })
                logger.info("主机: %s, %s = %s", host.name, setting.key, setting.value)
            else:
                results.append({
                    "AIIB.No": "2.3",
                    "Name": "Host must restrict direct MOB access",
                    "CIS.No": "3.3",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Config.HostAgent.plugins.solo.enableMob | Select Name, Value, Type, Description',
                    "Host": host.name,
                    "Value": {"key": "Config.HostAgent.plugins.solo.enableMob", "value": None, "type": None},
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 没有 Config.HostAgent.plugins.solo.enableMob 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.3",
                "Name": "Host must restrict direct MOB access",
                "CIS.No": "3.3",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Config.HostAgent.plugins.solo.enableMob | Select Name, Value, Type, Description',
                "Host": host.name,
                "Value": {"key": "Config.HostAgent.plugins.solo.enableMob", "value": None, "type": None},
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Config.HostAgent.plugins.solo.enableMob 设置失败: %s", host.name, e)

    container.Destroy()
    return results

def main(output_dir: str = None):
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_2.3_solo_enable_mob.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        solo_info = get_hosts_solo_enable_mob(content)
        export_to_json(solo_info, output_path)

if __name__ == "__main__":
    main()
