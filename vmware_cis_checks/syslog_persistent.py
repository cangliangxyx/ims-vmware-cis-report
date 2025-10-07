import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_syslog_info(content) -> List[Dict[str, Any]]:
    """
    收集所有主机的 Syslog.global.logDir 配置并检测状态
    :param content: vSphere service instance content
    :return: 每台主机的 Syslog 检查结果列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.logDir")
            if adv_settings:
                setting = adv_settings[0]
                value = setting.value or ""

                # 状态检测逻辑
                value_lower = value.lower() if value else ""
                if not value or "scratch" in value_lower or "tmp" in value_lower:
                    status = "Fail"
                else:
                    status = "Pass"

                results.append({
                    "AIIB.No": "3.1",
                    "Name": "Persistent Syslog Configuration (Read Only)",
                    "CIS.No": "4.1",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                    "Host": host.name,
                    "Value": value,
                    "Status": status,
                    "Description": (
                        "检测值: Syslog.global.logDir 指定持久化日志目录。"
                        "推荐配置为非易失性存储 (如 [datastore1]/systemlogs)，"
                        "若为空、指向 scratch/tmp 则为 Fail。"
                    ),
                    "Error": None
                })

                logger.info("[Syslog] 主机: %s | 值: %s | 状态: %s", host.name, value or "未配置", status)
            else:
                results.append({
                    "AIIB.No": "3.1",
                    "Name": "Persistent Syslog Configuration (Read Only)",
                    "CIS.No": "4.1",
                    "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                    "Host": host.name,
                    "Value": None,
                    "Status": "Fail",
                    "Description": "未配置 Syslog.global.logDir，日志未持久化存储。",
                    "Error": None
                })
                logger.warning("[Syslog] 主机 %s 未配置 Syslog.global.logDir", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.1",
                "Name": "Persistent Syslog Configuration (Read Only)",
                "CIS.No": "4.1",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "此主机不支持 Syslog.global.logDir 设置。",
                "Error": str(e)
            })
            logger.warning("[Syslog] 主机 %s 不支持 Syslog.global.logDir", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "3.1",
                "Name": "Persistent Syslog Configuration (Read Only)",
                "CIS.No": "4.1",
                "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDir',
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "获取 Syslog.global.logDir 配置失败。",
                "Error": str(e)
            })
            logger.error("[Syslog] 主机 %s 获取 Syslog.global.logDir 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机的 Syslog.global.logDir 配置，输出为一个统一 JSON 文件
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_3.1_syslog_persistent.json")

    # 从配置文件读取多 vCenter 信息
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data.get("HOST")
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            logger.info("[Syslog] 正在连接 vCenter: %s", vc_host)
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                syslog_results = collect_syslog_info(content)
                all_results.extend(syslog_results)
        except Exception as e:
            logger.error("[Syslog] 连接 vCenter %s 失败: %s", vc_host, e)
            all_results.append({
                "AIIB.No": "3.1",
                "Name": "Persistent Syslog Configuration (Read Only)",
                "CIS.No": "4.1",
                "CMD": "vCenter connection",
                "Host": vc_host,
                "Value": None,
                "Status": "Fail",
                "Description": "无法连接到 vCenter。",
                "Error": str(e)
            })

    export_to_json(all_results, output_path)
    logger.info("[Syslog] 所有主机的 Syslog.global.logDir 配置已导出到 %s", output_path)


if __name__ == "__main__":
    main()
