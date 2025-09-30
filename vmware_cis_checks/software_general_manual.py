import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_software_eogs(content) -> List[Dict[str, Any]]:
    """
    收集所有主机的软件 EOGS 检查项（手工验证）
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        results.append({
            "AIIB.No": "1.1",
            "Name": "Host software EOGS status (Manual)",
            "CIS.No": "2.1",
            "CMD": "Manual check required: verify ESXi version support status",
            "Host": host.name,
            "Value": None,
            "Status": "Pass",  # 默认 Pass，需人工确认
            "Description": "手工验证：确认主机运行的软件版本是否在 VMware 支持期内",
            "Error": None
        })
        logger.info("[EOGS] 主机 %s 需人工确认 ESXi 版本支持状态", host.name)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机的软件 EOGS 检查结果并合并输出到单个 JSON 文件
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_1.1_software_general_manual.json")

    # 读取 vCenter 列表
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data["HOST"]
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_software_eogs(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[EOGS] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[EOGS] 所有主机的软件支持状态已导出到 %s", output_path)


if __name__ == "__main__":
    main()
