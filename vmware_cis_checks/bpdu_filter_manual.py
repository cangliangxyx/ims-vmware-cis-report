import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_bpdu_filter(content) -> List[Dict[str, Any]]:
    """获取每台主机 BPDU 过滤状态 (需手工验证)"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        results.append({
            "AIIB.No": "4.3",
            "Name": "Host BPDU filtering must be manually verified",
            "CIS.No": "5.4",
            "CMD": "Manual check required; not exposed via API",
            "Host": host.name,
            "Value": None,
            "Description": "BPDU filtering must be checked manually",
            "Error": None
        })
        logger.info("主机 %s BPDU 检查需手工完成", host.name)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    输出每台主机 BPDU 过滤检查结果（手工验证）。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_4.3_bpdu_filter_manual.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        bpdu_info = get_hosts_bpdu_filter(content)
        export_to_json(bpdu_info, output_path)


if __name__ == "__main__":
    main()
