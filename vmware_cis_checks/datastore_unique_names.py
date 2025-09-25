import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_datastore_unique_names(content) -> List[Dict[str, Any]]:
    """
    检查每台主机的所有 Datastore 名称是否唯一
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            ds_names = []
            duplicates = []

            for ds in host.datastore:
                if ds.name in ds_names:
                    duplicates.append(ds.name)
                else:
                    ds_names.append(ds.name)

            results.append({
                "AIIB.No": "5.1",
                "Name": "Host must ensure all datastores have unique names (Manual)",
                "CIS.No": "6.2.2",
                "CMD": r'Get-Datastore | Select Name, VMHost',
                "Host": host.name,
                "Value": ds_names,
                "Duplicates": duplicates if duplicates else None,
                "Description": "Check that all datastores on host have unique names",
                "Error": None
            })
            if duplicates:
                logger.warning("主机 %s 存在重复 Datastore 名称: %s", host.name, duplicates)
            else:
                logger.info("主机 %s 所有 Datastore 名称唯一", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "5.1",
                "Name": "Host must ensure all datastores have unique names (Manual)",
                "CIS.No": "6.2.2",
                "CMD": r'Get-Datastore | Select Name, VMHost',
                "Host": host.name,
                "Value": None,
                "Duplicates": None,
                "Description": "Datastore retrieval error",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Datastore 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查所有主机的 Datastore 名称是否唯一并导出 JSON
    :param output_dir: 输出目录路径（默认 ../log）
    """
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_5.1_datastore_unique_names.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        ds_info = get_datastore_unique_names(content)
        export_to_json(ds_info, output_path)


if __name__ == "__main__":
    main()
