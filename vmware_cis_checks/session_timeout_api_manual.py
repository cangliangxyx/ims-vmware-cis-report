import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_session_timeout_api(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的 API 会话超时设置 (config.hostagent.vmacore.soap.sessiontimeout)
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Config.HostAgent.vmacore.soap.sessionTimeout")
            if adv_settings:
                setting = adv_settings[0]
                raw_value = {
                    "key": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__
                }
                results.append({
                    "AIIB.No": "2.12",
                    "Name": "Host must enforce API session timeout",
                    "CIS.No": "3.16",
                    "CMD": "host->configure->advanced system setting->Config.HostAgent.vmacore.soap.sessionTimeout",
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": """检测值: vSphere API SOAP 会话的超时时间（秒）。检测方法："value": "30"。""",
                    "Error": None
                })
                logger.info("主机 %s Config.HostAgent.vmacore.soap.sessionTimeout 原始值: %s", host.name, raw_value)
            else:
                results.append({
                    "AIIB.No": "2.12",
                    "Name": "Host must enforce API session timeout",
                    "CIS.No": "3.16",
                    "CMD": "Get-AdvancedSetting -Name Config.HostAgent.vmacore.soap.sessionTimeout",
                    "Host": host.name,
                    "Value": None,
                    "Description": "未找到该设置，表示使用默认值（可能无限制）",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Config.HostAgent.vmacore.soap.sessionTimeout", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "2.12",
                "Name": "Host must enforce API session timeout",
                "CIS.No": "3.16",
                "CMD": "Get-AdvancedSetting -Name Config.HostAgent.vmacore.soap.sessionTimeout",
                "Host": host.name,
                "Value": None,
                "Description": "此主机不支持 Config.HostAgent.vmacore.soap.sessionTimeout",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Config.HostAgent.vmacore.soap.sessionTimeout 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "2.12",
                "Name": "Host must enforce API session timeout",
                "CIS.No": "3.16",
                "CMD": "Get-AdvancedSetting -Name Config.HostAgent.vmacore.soap.sessionTimeout",
                "Host": host.name,
                "Value": None,
                "Description": "查询 API 会话超时设置失败",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Config.HostAgent.vmacore.soap.sessionTimeout 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    使用 VsphereConnection 获取 API session timeout 原始值并导出 JSON
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_2.12_session_timeout_api.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        session_timeout_info = get_hosts_session_timeout_api(content)
        export_to_json(session_timeout_info, output_path)
        logger.info("Config.HostAgent.vmacore.soap.sessionTimeout 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
