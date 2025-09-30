import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_bpdu_filter(content) -> List[Dict[str, Any]]:
    """
    检查每台主机 Net.BlockGuestBPDU 配置状态
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
                raw_value = {
                    "key": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__
                }
                results.append({
                    "AIIB.No": "4.3",
                    "Name": "Net.BlockGuestBPDU (Read Only)",
                    "CIS.No": "5.4",
                    "CMD": r"host-->configure->advanced system setting --> Net.BlockGuestBPDU",
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": "检测值: 启用 BPDU 过滤，检测方法：'value': 1",
                    "Error": None
                })
                logger.info("主机 %s Net.BlockGuestBPDU = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "4.3",
                    "Name": "Net.BlockGuestBPDU (Read Only)",
                    "CIS.No": "5.4",
                    "CMD": r"host-->configure->advanced system setting --> Net.BlockGuestBPDU",
                    "Host": host.name,
                    "Value": {"key": "Net.BlockGuestBPDU", "value": None, "type": None},
                    "Description": "未配置 Net.BlockGuestBPDU，建议显式设置为 1。",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Net.BlockGuestBPDU", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "4.3",
                "Name": "Net.BlockGuestBPDU (Read Only)",
                "CIS.No": "5.4",
                "CMD": r"host-->configure->advanced system setting --> Net.BlockGuestBPDU",
                "Host": host.name,
                "Value": None,
                "Description": "该主机不支持 Net.BlockGuestBPDU 设置",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Net.BlockGuestBPDU 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "4.3",
                "Name": "Net.BlockGuestBPDU (Read Only)",
                "CIS.No": "5.4",
                "CMD": r"host-->configure->advanced system setting --> Net.BlockGuestBPDU",
                "Host": host.name,
                "Value": None,
                "Description": "查询 Net.BlockGuestBPDU 失败",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Net.BlockGuestBPDU 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查主机 BPDU 过滤配置，并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_4.3_bpdu_filter.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        bpdu_info = get_hosts_bpdu_filter(content)
        export_to_json(bpdu_info, output_path)
        logger.info("Net.BlockGuestBPDU 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
