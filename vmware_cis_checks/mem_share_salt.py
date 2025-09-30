import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_mem_share_salt_info(content) -> List[Dict[str, Any]]:
    """
    收集每台主机的 Mem.ShareForceSalting 高级设置
    推荐值：2 (强制不同 VM 之间不共享 TPS 页面)
    :param content: vSphere service instance content
    :return: 每台主机的 Mem.ShareForceSalting 检查结果
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results: List[Dict[str, Any]] = []
    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Mem.ShareForceSalting")
            if adv_settings:
                setting = adv_settings[0]
                value = setting.value
                status = "Pass" if value == 2 else "Fail"

                results.append({
                    "AIIB.No": "1.4",
                    "Name": "Host must restrict inter-VM transparent page sharing (Automated)",
                    "CIS.No": "2.10",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description',
                    "Host": host.name,
                    "Value": value,
                    "Status": status,
                    "Description": "检测值：Mem.ShareForceSalting，推荐值为 2（强制不同 VM 之间不共享 TPS）",
                    "Error": None
                })
                logger.info("[MEM_SHARE_SALT] 主机 %s: Mem.ShareForceSalting=%s, Status=%s", host.name, value, status)
            else:
                results.append({
                    "AIIB.No": "1.4",
                    "Name": "Host must restrict inter-VM transparent page sharing (Automated)",
                    "CIS.No": "2.10",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description',
                    "Host": host.name,
                    "Value": None,
                    "Status": "Fail",
                    "Description": "Mem.ShareForceSalting 未配置",
                    "Error": None
                })
                logger.warning("[MEM_SHARE_SALT] 主机 %s 没有 Mem.ShareForceSalting 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "1.4",
                "Name": "Host must restrict inter-VM transparent page sharing (Automated)",
                "CIS.No": "2.10",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description',
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "Mem.ShareForceSalting 获取失败",
                "Error": str(e)
            })
            logger.error("[MEM_SHARE_SALT] 主机 %s 获取 Mem.ShareForceSalting 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机的 Mem.ShareForceSalting 配置，输出为一个 JSON 文件
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_1.4_mem_share_salt.json")

    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data["HOST"]
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_mem_share_salt_info(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[MEM_SHARE_SALT] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[MEM_SHARE_SALT] 所有主机的 Mem.ShareForceSalting 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
