import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_vmware_tools_prevent_recustomization_manual(content=None) -> List[Dict[str, Any]]:
    """
    手工检查：VMware Tools on deployed virtual machines must prevent being recustomized
    """
    results = []

    results.append({
        "AIIB.No": "7.3",
        "Name": "VMware Tools on deployed virtual machines must prevent being recustomized (Manual)",
        "CIS.No": "8.4",
        "CMD": None,
        "Host": None,
        "Value": None,
        "Description": "需要人工检查 VMware Tools 是否防止已部署 VM 被重新定制",
        "Error": None
    })

    logger.info("检查 7.3: VMware Tools 防止 VM 重新定制手工检查，无法自动化，已生成提示")
    return results


def main(output_dir: str = None):
    """
    手工检查 VMware Tools 防止 VM 重新定制并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_7.3_vmware_tools_prevent_recustomization_manual.json"

    vm_tools_recustom_info = get_vmware_tools_prevent_recustomization_manual()
    export_to_json(vm_tools_recustom_info, output_path)


if __name__ == "__main__":
    main()
