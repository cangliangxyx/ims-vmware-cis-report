import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_time_sync_info(content) -> List[Dict[str, Any]]:
    """
    收集主机时间同步服务状态（手工验证项）
    建议使用 NTP 或 PTP，并确保随主机启动并保持运行
    :param content: vSphere service instance content
    :return: 每台主机的时间同步检查结果列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        results.append({
            "AIIB.No": "1.3",
            "Name": "Host time synchronization service status (Manual)",
            "CIS.No": "2.7",
            "CMD": "Manual check required: verify NTP/PTP services are enabled and running",
            "Host": host.name,
            "Value": None,
            "Status": "Pass",  # 默认标记 Pass，需人工验证后调整
            "Description": "手工验证：确认主机时间同步服务（NTP/PTP）已启用并运行",
            "Error": None
        })
        logger.info("[TIME_SYNC] 主机 %s 时间同步服务需手工确认 (NTP/PTP)", host.name)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机的时间同步服务检查结果，输出为一个 JSON 文件
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_1.3_time_sync_manual.json")

    # 读取 vCenter 列表
    from config import settings
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data["HOST"]
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_time_sync_info(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[TIME_SYNC] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[TIME_SYNC] 所有主机的时间同步服务检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
