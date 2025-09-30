import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_password_max_days(content) -> List[Dict[str, Any]]:
    """
    收集每台主机 Security.PasswordMaxDays 配置
    推荐值：99999
    :param content: vSphere service instance content
    :return: 每台主机密码最大使用天数策略检查结果列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    results: List[Dict[str, Any]] = []

    for host in container.view:
        record = {
            "AIIB.No": "2.11",
            "Name": "Host must enforce maximum password age (Automated)",
            "CIS.No": "3.15",
            "CMD": r'Get-VMHost | Get-AdvancedSetting -Name Security.PasswordMaxDays',
            "Host": host.name,
            "Value": None,
            "Status": "Fail",
            "Description": '检测值: "value" == 99999',
            "Error": None
        }

        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Security.PasswordMaxDays")
            if adv_settings:
                setting = adv_settings[0]
                value = setting.value
                status = "Pass" if value is not None and int(value) == 99999 else "Fail"

                record.update({
                    "Value": {
                        "key": setting.key,
                        "value": value,
                        "type": type(value).__name__
                    },
                    "Status": status
                })
                logger.info("[PasswordMaxDays] 主机: %s, value=%s, Status=%s", host.name, value, status)
            else:
                logger.warning("[PasswordMaxDays] 主机 %s 未配置 Security.PasswordMaxDays 或不支持该设置", host.name)

        except vim.fault.InvalidName as e:
            record.update({
                "Value": {"key": "Security.PasswordMaxDays", "value": None, "type": None},
                "Status": "Fail",
                "Error": str(e)
            })
            logger.info("[PasswordMaxDays] 主机 %s 不支持 Security.PasswordMaxDays 设置", host.name)
        except Exception as e:
            record.update({
                "Value": {"key": "Security.PasswordMaxDays", "value": None, "type": None},
                "Status": "Fail",
                "Error": str(e)
            })
            logger.error("[PasswordMaxDays] 主机 %s 获取 Security.PasswordMaxDays 失败: %s", host.name, e)

        results.append(record)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机密码最大使用天数策略配置，输出为 JSON 文件
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_2.11_password_max_days.json")

    vsphere_data = settings.get_vsphere_config(os.getenv("project_env", "prod"))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_password_max_days(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[PasswordMaxDays] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[PasswordMaxDays] 所有主机密码最大使用天数策略检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
