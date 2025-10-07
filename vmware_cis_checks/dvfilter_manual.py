import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_dvfilter_settings(content) -> List[Dict[str, Any]]:
    """
    检查主机 dvFilter 网络 API 配置项 Net.DVFilterBindIpAddress
    推荐值：未配置（空值 ""），除非特定产品如 NSX 需要使用。
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Net.DVFilterBindIpAddress")

            if adv_settings:
                setting = adv_settings[0]
                value = str(setting.value).strip() if setting.value is not None else ""
            else:
                value = ""

            # 状态判定：空值为 Pass，非空为 Fail
            status = "Pass" if value == "" else "Fail"

            results.append({
                "AIIB.No": "4.2",
                "Name": "Host dvFilter API must be restricted (Manual)",
                "CIS.No": "5.3",
                "CMD": (
                    r"Get-VMHost | Get-AdvancedSetting -Name Net.DVFilterBindIpAddress "
                    r"| Select-Object Name, Value, Type, Description"
                ),
                "Host": host.name,
                "Value": value,
                "Status": status,
                "Description": (
                    f"检测值: Net.DVFilterBindIpAddress = '{value or '未配置'}' | "
                    "推荐值: 空值 (未配置)。仅当使用 NSX 等网络产品时才应配置此项。"
                ),
                "Error": None
            })

            logger.info("[dvFilter] 主机: %s | 值: %s | 状态: %s", host.name, value or "未配置", status)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "4.2",
                "Name": "Host dvFilter API must be restricted (Manual)",
                "CIS.No": "5.3",
                "CMD": (
                    r"Get-VMHost | Get-AdvancedSetting -Name Net.DVFilterBindIpAddress "
                    r"| Select-Object Name, Value, Type, Description"
                ),
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "该主机不支持 Net.DVFilterBindIpAddress 配置项。",
                "Error": str(e)
            })
            logger.info("[dvFilter] 主机 %s 不支持 Net.DVFilterBindIpAddress 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "4.2",
                "Name": "Host dvFilter API must be restricted (Manual)",
                "CIS.No": "5.3",
                "CMD": (
                    r"Get-VMHost | Get-AdvancedSetting -Name Net.DVFilterBindIpAddress "
                    r"| Select-Object Name, Value, Type, Description"
                ),
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "获取 Net.DVFilterBindIpAddress 失败。",
                "Error": str(e)
            })
            logger.error("[dvFilter] 主机 %s 获取 Net.DVFilterBindIpAddress 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，检查所有主机的 Net.DVFilterBindIpAddress 并导出为 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_4.2_dvfilter_manual.json")

    # 读取 vCenter 配置
    vsphere_data = settings.get_vsphere_config(os.getenv("project_env", "prod"))
    vc_list = vsphere_data.get("HOST", [])
    if not isinstance(vc_list, list):
        vc_list = [vc_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in vc_list:
        try:
            logger.info("[dvFilter] 正在连接 vCenter: %s", vc_host)
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_dvfilter_settings(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[dvFilter] 无法连接 vCenter %s: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[dvFilter] 所有主机 dvFilter API 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
