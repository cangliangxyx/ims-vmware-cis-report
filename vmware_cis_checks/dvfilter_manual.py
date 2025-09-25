import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_dvfilter(content) -> List[Dict[str, Any]]:
    """获取每台主机的 dvFilter API 配置 (手工检查是否被限制)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Net.DVFilterBindIpAddress")
            value = adv_settings[0].value if adv_settings else None

            results.append({
                "AIIB.No": "4.2",
                "Name": "Host dvFilter API must be restricted (Manual)",
                "CIS.No": "5.3",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Net.DVFilterBindIpAddress | Select-Object Name, Value, Type, Description',
                "Host": host.name,
                "Value": value,
                "Description": "dvFilter network API bind IP",
                "Error": None
            })
            logger.info("主机 %s dvFilter 配置: %s", host.name, value)

        except Exception as e:
            results.append({
                "AIIB.No": "4.2",
                "Name": "Host dvFilter API must be restricted (Manual)",
                "CIS.No": "5.3",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Net.DVFilterBindIpAddress | Select-Object Name, Value, Type, Description',
                "Host": host.name,
                "Value": None,
                "Description": "dvFilter network API bind IP (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 dvFilter 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    获取所有主机 dvFilter 配置并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_4.2_dvfilter_manual.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        dvfilter_info = get_hosts_dvfilter(content)
        export_to_json(dvfilter_info, output_path)


if __name__ == "__main__":
    main()
