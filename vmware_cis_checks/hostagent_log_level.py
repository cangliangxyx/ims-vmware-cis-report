import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_hostagent_log_level(content) -> List[Dict[str, Any]]:
    """
    检查所有主机的 Config.HostAgent.log.level 配置，并增加状态字段。
    对应安全基线项：4.4 (L1) Host must set the logging informational level to info
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Config.HostAgent.log.level")

            if adv_settings:
                setting = adv_settings[0]
                value = setting.value.strip() if setting.value else ""

                # 状态判断逻辑：推荐值为 "info"
                if value.lower() == "info":
                    status = "Pass"
                else:
                    status = "Fail"

                results.append({
                    "AIIB.No": "3.3",
                    "Name": "Host must set the logging informational level to info",
                    "CIS.No": "4.4",
                    "CMD": "host -> configure -> advanced system setting -> Config.HostAgent.log.level",
                    "Host": host.name,
                    "Value": value,
                    "Status": status,
                    "Description": (
                        f"检测值: Config.HostAgent.log.level = '{value or '未配置'}' | "
                        "推荐值: 日志级别 'info' "
                    ),
                    "Error": None
                })

                logger.info("[HostAgent Log] 主机: %s | 值: %s | 状态: %s", host.name, value or "未配置", status)

            else:
                results.append({
                    "AIIB.No": "3.3",
                    "Name": "Host must set the logging informational level to info",
                    "CIS.No": "4.4",
                    "CMD": "host -> configure -> advanced system setting -> Config.HostAgent.log.level",
                    "Host": host.name,
                    "Value": None,
                    "Status": "Fail",
                    "Description": "未配置 Config.HostAgent.log.level，建议显式设置为 'info'。",
                    "Error": None
                })
                logger.warning("[HostAgent Log] 主机 %s 未配置 Config.HostAgent.log.level", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.3",
                "Name": "Host must set the logging informational level to info",
                "CIS.No": "4.4",
                "CMD": "host -> configure -> advanced system setting -> Config.HostAgent.log.level",
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "该主机不支持 Config.HostAgent.log.level 配置项。",
                "Error": str(e)
            })
            logger.info("[HostAgent Log] 主机 %s 不支持 Config.HostAgent.log.level 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "3.3",
                "Name": "Host must set the logging informational level to info",
                "CIS.No": "4.4",
                "CMD": "host -> configure -> advanced system setting -> Config.HostAgent.log.level",
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "获取 Config.HostAgent.log.level 失败。",
                "Error": str(e)
            })
            logger.error("[HostAgent Log] 主机 %s 获取 Config.HostAgent.log.level 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，检查所有主机的 Config.HostAgent.log.level 并导出为 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_3.3_hostagent_log_level.json")

    # 读取 vCenter 列表
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_hostagent_log_level(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[HostAgent Log] 无法连接 vCenter %s: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[HostAgent Log] 所有主机 Config.HostAgent.log.level 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
