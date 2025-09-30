import os
import logging
import csv
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_all_advanced_settings(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的所有 Advanced System Settings
    返回列表，每个元素对应一台主机
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions()
            host_settings = [
                {"key": setting.key, "value": setting.value, "type": type(setting.value).__name__}
                for setting in adv_settings
            ]

            results.append({"Host": host.name, "AdvancedSettings": host_settings, "Error": None})
            logger.info("主机 %s 获取到 %d 条高级设置", host.name, len(host_settings))

        except Exception as e:
            results.append({"Host": host.name, "AdvancedSettings": [], "Error": str(e)})
            logger.error("主机 %s 获取高级设置失败: %s", host.name, e)

    container.Destroy()
    return results


def export_host_json_csv(host_data: Dict[str, Any], output_dir: str):
    """
    将单台主机高级设置导出为 JSON 和 CSV
    """
    host_name = host_data["Host"]
    settings = host_data["AdvancedSettings"]

    # JSON 导出
    json_file = os.path.join(output_dir, f"no_0.0_{host_name}_advanced_system_setting.json")
    export_to_json(host_data, json_file)
    logger.info("主机 %s 高级设置 JSON 已导出到 %s", host_name, json_file)

    # CSV 导出
    csv_file = os.path.join(output_dir, f"no_0.0_{host_name}_advanced_system_setting.csv")
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "value", "type"])
        writer.writeheader()
        for setting in settings:
            writer.writerow(setting)
    logger.info("主机 %s 高级设置 CSV 已导出到 %s", host_name, csv_file)


def main(output_dir: str = None):
    # 设置默认输出目录
    output_dir = output_dir or "./log"
    os.makedirs(output_dir, exist_ok=True)

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        all_hosts_settings = get_all_advanced_settings(content)

        # 针对每台主机导出独立 JSON 和 CSV
        for host_data in all_hosts_settings:
            export_host_json_csv(host_data, output_dir)


if __name__ == "__main__":
    main()
