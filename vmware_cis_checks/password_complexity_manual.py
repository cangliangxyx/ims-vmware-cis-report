import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_password_quality_control(content) -> List[Dict[str, Any]]:
    """
    收集每台主机 Security.PasswordQualityControl 配置
    推荐值：包含 min=disabled,disabled,disabled,disabled,14
    :param content: vSphere service instance content
    :return: 每台主机密码复杂性检查结果列表
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    results: List[Dict[str, Any]] = []

    for host in container.view:
        record = {
            "AIIB.No": "2.7",
            "Name": "Host must enforce password complexity",
            "CIS.No": "3.11",
            "CMD": "Get-AdvancedSetting -Name Security.PasswordQualityControl",
            "Host": host.name,
            "Value": None,
            "Status": "Fail",
            "Description": '检测值:主机密码复杂性规则。"value" 是否包含 min=disabled,disabled,disabled,disabled,14',
            "Error": None
        }

        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Security.PasswordQualityControl")
            if adv_settings:
                setting = adv_settings[0]
                value = setting.value or ""
                status = "Pass" if "min=disabled,disabled,disabled,disabled,14" in str(value) else "Fail"

                record.update({
                    "Value": {
                        "key": setting.key,
                        "value": value,
                        "type": type(setting.value).__name__
                    },
                    "Status": status
                })

                logger.info("[PasswordQuality] 主机: %s, value=%s, Status=%s", host.name, value, status)
            else:
                logger.warning("[PasswordQuality] 主机 %s 未找到 Security.PasswordQualityControl 设置", host.name)

        except Exception as e:
            record.update({
                "Value": None,
                "Status": "Fail",
                "Error": str(e)
            })
            logger.error("[PasswordQuality] 主机 %s 查询 Security.PasswordQualityControl 失败: %s", host.name, e)

        results.append(record)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，收集所有主机密码复杂性配置，输出为 JSON 文件
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_2.7_password_quality_control.json")

    vsphere_data = settings.get_vsphere_config(os.getenv("project_env", "prod"))
    host_list = vsphere_data.get("HOST", [])
    if not isinstance(host_list, list):
        host_list = [host_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_password_quality_control(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[PasswordQuality] 连接 vCenter %s 失败: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[PasswordQuality] 所有主机密码复杂性检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
