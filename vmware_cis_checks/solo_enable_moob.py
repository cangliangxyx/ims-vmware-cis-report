import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_solo_enable_mob_info(content) -> List[Dict[str, Any]]:
    """
    收集每台主机 Config.HostAgent.plugins.solo.enableMob 高级设置
    推荐值：False（禁用）
    :param content: vSphere service instance content
    :return: 每台主机设置检查结果列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    results: List[Dict[str, Any]] = []

    for host in container.view:
        record = {
            "AIIB.No": "2.3",
            "Name": "Host must restrict direct MOB access",
            "CIS.No": "3.3",
            "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Config.HostAgent.plugins.solo.enableMob | '
                   r'Select Name, Value, Type, Description',
            "Host": host.name,
            "Value": None,
            "Status": "Fail",
            "Description": "Config.HostAgent.plugins.solo.enableMob not checked, 检测值:'value': false",
            "Error": None
        }

        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Config.HostAgent.plugins.solo.enableMob")
            if adv_settings:
                setting = adv_settings[0]
                status = "Pass" if str(setting.value).lower() in ["false", "0"] else "Fail"
                record.update({
                    "Value": {
                        "key": setting.key,
                        "value": setting.value,
                        "type": type(setting.value).__name__
                    },
                    "Status": status,
                    "Description": "Direct MOB access should be disabled"
                })
                logger.info("[MOB] 主机: %s, %s = %s, Status: %s", host.name, setting.key, setting.value, status)
            else:
                record.update({
                    "Value": {"key": "Config.HostAgent.plugins.solo.enableMob", "value": None, "type": None},
                    "Status": "Fail",
                    "Description": "Not configured"
                })
                logger.warning("[MOB] 主机 %s 没有 Config.HostAgent.plugins.solo.enableMob 设置", host.name)

        except Exception as e:
            record.update({
                "Value": {"key": "Config.HostAgent.plugins.solo.enableMob", "value": None, "type": None},
                "Status": "Fail",
                "Description": "Error retrieving setting",
                "Error": str(e)
            })
            logger.error("[MOB] 主机 %s 获取设置失败: %s", host.name, e)

        results.append(record)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机 MOB 设置状态，输出为 JSON 文件
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_2.3_solo_enable_mob.json")

    vsphere_data = settings.get_vsphere_config(os.getenv("project_env", "prod"))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_solo_enable_mob_info(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[MOB] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[MOB] 所有主机 Config.HostAgent.plugins.solo.enableMob 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
