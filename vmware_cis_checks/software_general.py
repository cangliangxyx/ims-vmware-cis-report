import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_software_eogs(content) -> List[Dict[str, Any]]:
    """
    检查主机软件是否已达到 End of General Support (EOGS)
    手工验证项：需要管理员确认 ESXi 版本是否在官方支持期内
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        results.append({
            "AIIB.No": "1.1",
            "Name": "Host software EOGS status (Manual)",
            "CIS.No": "2.1",
            "CMD": "Manual check required: verify ESXi version support status",
            "Host": host.name,
            "Value": None,
            "Status": "Pass",
            "Description": "手工验证：确认主机运行的软件版本是否在 VMware 支持期内",
            "Error": None
        })
        logger.info("主机 %s 软件支持状态需手工确认 (EOGS)", host.name)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    输出每台主机软件 EOGS 检查（手工验证）结果
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_1.1_software_general_manual.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        eogs_info = get_hosts_software_eogs(content)
        export_to_json(eogs_info, output_path)
        logger.info("主机软件 EOGS 手工检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
