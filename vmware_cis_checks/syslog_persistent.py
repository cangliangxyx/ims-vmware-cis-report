import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_syslog_persistent(content) -> List[Dict[str, Any]]:
    """查看每台主机的 Syslog.global.logDir 配置（只读）"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logDir")
            if adv_settings:
                setting = adv_settings[0]
                results.append({
                    "AIIB.No": "3.1",
                    "Name": "Persistent Syslog Configuration (Read Only)",
                    "CIS.No": "4.1",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                    "Host": host.name,
                    "Value": setting.value,
                    "Description": "Persistent syslog directory",
                    "Error": None
                })
                logger.info("主机: %s, Syslog.global.logDir = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "3.1",
                    "Name": "Persistent Syslog Configuration (Read Only)",
                    "CIS.No": "4.1",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                    "Host": host.name,
                    "Value": None,
                    "Description": "Not configured",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Syslog.global.logDir", host.name)
        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.1",
                "Name": "Persistent Syslog Configuration (Read Only)",
                "CIS.No": "5.1",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                "Host": host.name,
                "Value": None,
                "Description": "Setting not supported on this host",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Syslog.global.logDir 设置", host.name)
        except Exception as e:
            results.append({
                "AIIB.No": "3.1",
                "Name": "Persistent Syslog Configuration (Read Only)",
                "CIS.No": "4.1",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                "Host": host.name,
                "Value": None,
                "Description": "Error retrieving syslog configuration",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Syslog.global.logDir 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查主机 Syslog 持久化配置并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    # 设置默认输出目录
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_3.1_syslog_persistent.json"

    # 获取数据并导出
    with VsphereConnection() as si:
        content = si.RetrieveContent()
        syslog_info = get_hosts_syslog_persistent(content)
        export_to_json(syslog_info, output_path)


if __name__ == "__main__":
    main()
