import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings  # 假设 settings.get_vsphere_config 可获取多 vCenter 配置

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_disabled_protocols(content) -> List[Dict[str, Any]]:
    """
    收集每台主机禁用协议配置
    推荐值：SSLv3,TLSv1.0,TLSv1.1 必须在列表中
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    results: List[Dict[str, Any]] = []

    expected_protocols = {"sslv3", "tlsv1", "tlsv1.1"}

    for host in container.view:
        record = {
            "AIIB.No": "2.16",
            "Name": "Disabled Protocols (Read Only)",
            "CIS.No": "3.26",
            "CMD": "host-->configure->advanced system setting --> UserVars.ESXiVPsDisabledProtocols",
            "Host": host.name,
            "Value": None,
            "Status": "Fail",
            "Description": '检测值: "value" 包含 SSLv3,TLSv1.0,TLSv1.1',
            "Error": None
        }

        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("UserVars.ESXiVPsDisabledProtocols")
            if adv_settings:
                setting = adv_settings[0]
                value = setting.value
                if isinstance(value, str):
                    protocols = {p.strip() for p in value.split(",")}
                elif isinstance(value, list):
                    protocols = set(value)
                else:
                    protocols = set()

                status = "Pass" if expected_protocols.issubset(protocols) else "Fail"

                record.update({
                    "Value": {"key": setting.key, "value": value, "type": type(value).__name__},
                    "Status": status
                })
                logger.info("[DisabledProtocols] 主机: %s, protocols=%s, Status=%s", host.name, protocols, status)
            else:
                logger.warning("[DisabledProtocols] 主机 %s 未配置禁用协议", host.name)

        except vim.fault.InvalidName as e:
            record.update({
                "Value": {"key": "UserVars.ESXiVPsDisabledProtocols", "value": None, "type": None},
                "Status": "Fail",
                "Error": str(e)
            })
            logger.info("[DisabledProtocols] 主机 %s 不支持禁用协议设置", host.name)
        except Exception as e:
            record.update({
                "Value": {"key": "UserVars.ESXiVPsDisabledProtocols", "value": None, "type": None},
                "Status": "Fail",
                "Error": str(e)
            })
            logger.error("[DisabledProtocols] 主机 %s 查询失败: %s", host.name, e)

        results.append(record)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机禁用协议配置，统一导出 JSON
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_2.16_tls_version.json")

    # 获取 vCenter 列表
    vsphere_data = settings.get_vsphere_config(os.getenv("project_env", "prod"))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_disabled_protocols(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[DisabledProtocols] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[DisabledProtocols] 所有主机检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
