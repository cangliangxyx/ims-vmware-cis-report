import os
import logging
from typing import List, Dict
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_vmware_tools_prevent_recustomization_manual(content=None) -> List[Dict]:
    """
    VMware Tools on deployed virtual machines must prevent being recustomized (默认通过)
    """
    results: List[Dict] = [{
        "AIIB.No": "7.3",
        "Name": "VMware Tools on deployed virtual machines must prevent being recustomized",
        "CIS.No": "8.4",
        "CMD": None,
        "Host": "ALL_HOSTS",
        "Value": "默认通过（需人工确认）",
        "Status": "Pass",
        "Description": "默认假定 VMware Tools 已配置防止已部署 VM 被重新定制，需要人工验证",
        "Error": None
    }]
    logger.info("[7.3] VMware Tools 防止 VM 重新定制默认通过检查")
    return results


def main(output_dir: str = None):
    """
    导出 VMware Tools 防止 VM 重新定制检查 JSON
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_7.3_vmware_tools_prevent_recustomization_manual.json")

    results = get_vmware_tools_prevent_recustomization_manual()
    export_to_json(results, output_path)
    logger.info("[7.3] 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
