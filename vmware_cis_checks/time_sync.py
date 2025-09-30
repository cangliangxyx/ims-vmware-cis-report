import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_time_sync(content) -> List[Dict[str, Any]]:
    """
    检查主机时间同步服务是否启用并运行 (手工验证)
    建议使用 NTP 或 PTP，并确保随主机启动并保持运行
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
            "Description": "手工验证：确认主机时间同步服务（NTP/PTP）已启用并运行",
            "Error": None
        })
        logger.info("主机 %s 时间同步服务需手工确认 (NTP/PTP)", host.name)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    输出每台主机时间同步服务检查（手工验证）结果
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_1.3_time_sync_manual.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        time_sync_info = get_hosts_time_sync(content)
        export_to_json(time_sync_info, output_path)
        logger.info("主机时间同步服务手工检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
