import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_bpdu_filter(content) -> List[Dict[str, Any]]:
    """
    检查每台主机 Net.BlockGuestBPDU 配置状态。
    推荐值：1（启用 BPDU 过滤）
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Net.BlockGuestBPDU")

            if adv_settings:
                setting = adv_settings[0]
                value = str(setting.value).strip() if setting.value is not None else ""
                status = "Pass" if value == "1" else "Fail"

                results.append({
                    "AIIB.No": "4.3",
                    "Name": "Host must filter Bridge Protocol Data Unit (BPDU) packets (Manual)",
                    "CIS.No": "5.4",
                    "CMD": "host -> configure -> advanced system setting -> Net.BlockGuestBPDU",
                    "Host": host.name,
                    "Value": value,
                    "Status": status,
                    "Description": (
                        f"检测值: Net.BlockGuestBPDU = '{value or '未配置'}' | "
                        "推荐值: '1' (启用 BPDU 过滤以防止环路与上联锁死)"
                    ),
                    "Error": None
                })

                logger.info("[BPDU Filter] 主机: %s | 值: %s | 状态: %s", host.name, value or "未配置", status)

            else:
                results.append({
                    "AIIB.No": "4.3",
                    "Name": "Host must filter Bridge Protocol Data Unit (BPDU) packets (Manual)",
                    "CIS.No": "5.4",
                    "CMD": "host -> configure -> advanced system setting -> Net.BlockGuestBPDU",
                    "Host": host.name,
                    "Value": None,
                    "Status": "Fail",
                    "Description": "未配置 Net.BlockGuestBPDU，建议显式设置为 1。",
                    "Error": None
                })
                logger.warning("[BPDU Filter] 主机 %s 未配置 Net.BlockGuestBPDU", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "4.3",
                "Name": "Host must filter Bridge Protocol Data Unit (BPDU) packets (Manual)",
                "CIS.No": "5.4",
                "CMD": "host -> configure -> advanced system setting -> Net.BlockGuestBPDU",
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "该主机不支持 Net.BlockGuestBPDU 配置项。",
                "Error": str(e)
            })
            logger.info("[BPDU Filter] 主机 %s 不支持 Net.BlockGuestBPDU 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "4.3",
                "Name": "Host must filter Bridge Protocol Data Unit (BPDU) packets (Manual)",
                "CIS.No": "5.4",
                "CMD": "host -> configure -> advanced system setting -> Net.BlockGuestBPDU",
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "获取 Net.BlockGuestBPDU 失败。",
                "Error": str(e)
            })
            logger.error("[BPDU Filter] 主机 %s 获取 Net.BlockGuestBPDU 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，检查所有主机的 BPDU 过滤配置，并导出为 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_4.3_bpdu_filter.json")

    # 获取 vCenter 列表
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    vc_list = vsphere_data.get("HOST", [])
    if not isinstance(vc_list, list):
        vc_list = [vc_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in vc_list:
        try:
            logger.info("[BPDU Filter] 正在连接 vCenter: %s", vc_host)
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_bpdu_filter(content)
                # 在结果中追加 vCenter 名称，方便区分
                for r in results:
                    r["VCenter"] = vc_host
                all_results.extend(results)
        except Exception as e:
            logger.error("[BPDU Filter] 无法连接 vCenter %s: %s", vc_host, e)
            all_results.append({
                "VCenter": vc_host,
                "Host": None,
                "Status": "Fail",
                "Description": "无法连接到 vCenter",
                "Error": str(e)
            })

    export_to_json(all_results, output_path)
    logger.info("[BPDU Filter] 所有主机 Net.BlockGuestBPDU 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
