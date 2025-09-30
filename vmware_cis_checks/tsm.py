import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_tsm_service_info(content) -> List[Dict[str, Any]]:
    """
    收集每台主机的 TSM（ESXi Shell）服务状态
    推荐值：Stopped / 手动启动
    :param content: vSphere service instance content
    :return: 每台主机 TSM 服务检查结果列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    results: List[Dict[str, Any]] = []

    for host in container.view:
        record = {
            "AIIB.No": "2.2",
            "Name": "Host must deactivate the ESXi shell (Automated)",
            "CIS.No": "3.2",
            "CMD": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM" } | '
                   r'Select Key, Label, Policy, Running, Required',
            "Host": host.name,
            "Value": None,
            "Status": "Fail",
            "Description": "TSM service not checked，检测值:'policy': off, 'running': false,",
            "Error": None
        }

        try:
            service = next((s for s in host.configManager.serviceSystem.serviceInfo.service if s.key == "TSM"), None)

            if service:
                status = "Pass" if service.policy.lower() == "off" else "Fail"
                record.update({
                    "Value": {
                        "key": service.key,
                        "label": service.label,
                        "policy": service.policy,
                        "running": service.running,
                        "required": service.required
                    },
                    "Status": status,
                    "Description": "TSM (ESXi Shell) service status, should be stopped / manual start"
                })
                logger.info("[TSM] 主机: %s, TSM运行状态: %s, 策略: %s, Status: %s",
                            host.name, service.running, service.policy, status)
            else:
                record.update({
                    "Description": "TSM service not found",
                    "Status": "Fail"
                })
                logger.warning("[TSM] 主机 %s 没有找到 TSM 服务", host.name)

        except Exception as e:
            record.update({
                "Description": "TSM service (Error)",
                "Status": "Fail",
                "Error": str(e)
            })
            logger.error("[TSM] 主机 %s 获取 TSM 服务状态失败: %s", host.name, e)

        results.append(record)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机 TSM 服务状态，输出为 JSON 文件
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_2.2_tsm.json")

    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_tsm_service_info(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[TSM] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[TSM] 所有主机 TSM 服务检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
