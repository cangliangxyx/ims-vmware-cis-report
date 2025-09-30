import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings  # 假设 settings.get_vsphere_config 可获取多 vCenter 配置

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_api_session_timeout(content) -> List[Dict[str, Any]]:
    """
    收集每台主机 Config.HostAgent.vmacore.soap.sessionTimeout 配置
    推荐值：30
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    results: List[Dict[str, Any]] = []

    for host in container.view:
        record = {
            "AIIB.No": "2.12",
            "Name": "Host must enforce API session timeout",
            "CIS.No": "3.16",
            "CMD": "host->configure->advanced system setting->Config.HostAgent.vmacore.soap.sessionTimeout",
            "Host": host.name,
            "Value": None,
            "Status": "Fail",
            "Description": '检测值: "value" == 30',
            "Error": None
        }

        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Config.HostAgent.vmacore.soap.sessionTimeout")
            if adv_settings:
                setting = adv_settings[0]
                value = setting.value
                status = "Pass" if value is not None and int(value) == 30 else "Fail"

                record.update({
                    "Value": {
                        "key": setting.key,
                        "value": value,
                        "type": type(value).__name__
                    },
                    "Status": status
                })
                logger.info("[API Session Timeout] 主机: %s, value=%s, Status=%s", host.name, value, status)
            else:
                logger.warning("[API Session Timeout] 主机 %s 未配置 Config.HostAgent.vmacore.soap.sessionTimeout，使用默认值", host.name)

        except vim.fault.InvalidName as e:
            record.update({
                "Value": {"key": "Config.HostAgent.vmacore.soap.sessionTimeout", "value": None, "type": None},
                "Status": "Fail",
                "Error": str(e)
            })
            logger.info("[API Session Timeout] 主机 %s 不支持该设置", host.name)
        except Exception as e:
            record.update({
                "Value": {"key": "Config.HostAgent.vmacore.soap.sessionTimeout", "value": None, "type": None},
                "Status": "Fail",
                "Error": str(e)
            })
            logger.error("[API Session Timeout] 主机 %s 查询失败: %s", host.name, e)

        results.append(record)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机 API 会话超时策略配置，统一导出 JSON
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_2.12_session_timeout_api.json")

    vsphere_data = settings.get_vsphere_config(os.getenv("project_env", "prod"))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_api_session_timeout(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[API Session Timeout] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[API Session Timeout] 所有主机检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
