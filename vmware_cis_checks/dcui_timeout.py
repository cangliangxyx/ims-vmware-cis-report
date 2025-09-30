import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_dcui_timeout_info(content) -> List[Dict[str, Any]]:
    """
    收集每台主机的 DCUI timeout 配置
    推荐值：大于 0 秒
    :param content: vSphere service instance content
    :return: 每台主机 DCUI timeout 检查结果列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    results: List[Dict[str, Any]] = []

    for host in container.view:
        record = {
            "AIIB.No": "2.5",
            "Name": "Host must automatically terminate idle DCUI sessions (Automated)",
            "CIS.No": "3.7",
            "CMD": r"Get-VMHost | Get-AdvancedSetting -Name UserVars.DcuiTimeOut",
            "Host": host.name,
            "Value": None,
            "Status": "Fail",
            "Description": "snmp_service.running = True → 'running'; snmp_service.running = False → 'stopped'; 检测方法：'running': false",
            "Error": None
        }

        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("UserVars.DcuiTimeOut")
            if adv_settings:
                setting = adv_settings[0]
                timeout_value = int(setting.value) if setting.value is not None else 0
                status = "Pass" if timeout_value > 0 else "Fail"

                record.update({
                    "Value": {
                        "key": setting.key,
                        "value": setting.value,
                        "type": type(setting.value).__name__
                    },
                    "Status": status,
                    "Description": "snmp_service.running = True → 'running'; snmp_service.running = False → 'stopped'; 检测方法：'running': false"
                })
                logger.info("[DCUI] 主机: %s, UserVars.DcuiTimeOut=%s, Status=%s", host.name, setting.value, status)
            else:
                logger.warning("[DCUI] 主机 %s 未配置 UserVars.DcuiTimeOut", host.name)
        except Exception as e:
            record.update({
                "Value": None,
                "Status": "Fail",
                "Error": str(e)
            })
            logger.error("[DCUI] 主机 %s 查询 UserVars.DcuiTimeOut 失败: %s", host.name, e)

        results.append(record)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机 DCUI timeout 配置，输出为 JSON 文件
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_2.5_dcui_timeout.json")

    vsphere_data = settings.get_vsphere_config(os.getenv("project_env", "prod"))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_dcui_timeout_info(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[DCUI] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[DCUI] 所有主机 DCUI timeout 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
