import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_hostagent_log_level(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的 Config.HostAgent.log.level 配置，并检查是否为 "info"
    :param content: vSphere API content 对象
    :return: 包含每台主机日志级别检查结果的列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Config.HostAgent.log.level")
            if adv_settings:
                setting = adv_settings[0]
                raw_value = {
                    "key": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__
                }
                results.append({
                    "AIIB.No": "4.4",
                    "Name": "Config.HostAgent.log.level (Read Only)",
                    "CIS.No": "4.4",
                    "CMD": r'host-->configure->advanced system setting --> config.hostagent.log.level',
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": """检测值: Host Agent 日志级别配置。检测方法："value": 'info'""",
                    "Error": None
                })
                logger.info("主机 %s Config.HostAgent.log.level = %s (符合: %s)", host.name, raw_value)
            else:
                results.append({
                    "AIIB.No": "4.4",
                    "Name": "Config.HostAgent.log.level (Read Only)",
                    "CIS.No": "4.4",
                    "CMD": r'host-->configure->advanced system setting --> config.hostagent.log.level',
                    "Host": host.name,
                    "Value": {"key": "Config.HostAgent.log.level", "value": None, "type": None},
                    "Compliant": False,
                    "Description": "未配置 Config.HostAgent.log.level，建议显式设置为 info。",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Config.HostAgent.log.level", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "4.4",
                "Name": "Config.HostAgent.log.level (Read Only)",
                "CIS.No": "4.4",
                "CMD": r'host-->configure->advanced system setting --> config.hostagent.log.level',
                "Host": host.name,
                "Value": None,
                "Compliant": False,
                "Description": "该主机不支持 Config.HostAgent.log.level 设置",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Config.HostAgent.log.level 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "4.4",
                "Name": "Config.HostAgent.log.level (Read Only)",
                "CIS.No": "4.4",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Config.HostAgent.log.level',
                "Host": host.name,
                "Value": None,
                "Compliant": False,
                "Description": "查询 Config.HostAgent.log.level 失败",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Config.HostAgent.log.level 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查 Config.HostAgent.log.level 是否为 info 并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_4.4_hostagent_log_level.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        loglevel_info = get_hosts_hostagent_log_level(content)
        export_to_json(loglevel_info, output_path)
        logger.info("Config.HostAgent.log.level 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
