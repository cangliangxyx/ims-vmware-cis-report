import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_disabled_protocols(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的禁用协议配置 (UserVars.ESXiVPsDisabledProtocols)
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("UserVars.ESXiVPsDisabledProtocols")
            if adv_settings:
                setting = adv_settings[0]
                raw_value = {
                    "key": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__
                }
                results.append({
                    "AIIB.No": "2.16",
                    "Name": "Disabled Protocols (Read Only)",
                    "CIS.No": "3.26",
                    "CMD": "host-->configure->advanced system setting --> UserVars.ESXiVPsDisabledProtocols",
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": """检测值: 指定禁用的协议列表，检测方法："value": 'SSLv3,TLSv1.0,TLSv1.1'。""",
                    "Error": None
                })
                logger.info("主机 %s 禁用协议值: %s", host.name, raw_value)
            else:
                results.append({
                    "AIIB.No": "2.16",
                    "Name": "Disabled Protocols (Read Only)",
                    "CIS.No": "3.26",
                    "CMD": "Get-VMHost | Get-AdvancedSetting -Name UserVars.ESXiVPsDisabledProtocols",
                    "Host": host.name,
                    "Value": {"key": "UserVars.ESXiVPsDisabledProtocols", "value": None, "type": None},
                    "Description": "未配置禁用协议，可能允许使用弱协议",
                    "Error": None
                })
                logger.warning("主机 %s 未配置禁用协议", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "2.16",
                "Name": "Disabled Protocols (Read Only)",
                "CIS.No": "3.26",
                "CMD": "Get-AdvancedSetting -Name UserVars.ESXiVPsDisabledProtocols",
                "Host": host.name,
                "Value": None,
                "Description": "此主机不支持 UserVars.ESXiVPsDisabledProtocols 设置",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持禁用协议设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "2.16",
                "Name": "Disabled Protocols (Read Only)",
                "CIS.No": "3.26",
                "CMD": "Get-AdvancedSetting -Name UserVars.ESXiVPsDisabledProtocols",
                "Host": host.name,
                "Value": None,
                "Description": "查询禁用协议配置失败",
                "Error": str(e)
            })
            logger.error("主机 %s 获取禁用协议配置失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查主机禁用协议配置并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_2.16_tls_version.json.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        disabled_protocols_info = get_hosts_disabled_protocols(content)
        export_to_json(disabled_protocols_info, output_path)
        logger.info("禁用协议配置检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
