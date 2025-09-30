import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_all_advanced_settings(content) -> List[Dict[str, Any]]:
    """
    获取每台主机的所有 Advanced System Settings
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


def main(output_dir: str = None):
    # 设置默认输出目录
    if output_dir is None:
        output_dir = "./log"
    output_path = f"{output_dir}/no_0.0_advanced_system_setting.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        all_settings = get_all_advanced_settings(content)
        export_to_json(all_settings, output_path)
        logger.info("所有主机高级设置已导出到 %s", output_path)


if __name__ == "__main__":
    main()
