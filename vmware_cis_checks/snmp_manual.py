import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_hosts_snmp_manual(content=None) -> List[Dict[str, Any]]:
    """
    手工检查：Host should deactivate SNMP
    注意：SNMP 配置无法直接通过 API 自动判断，需要人工确认
    """
    results = []

    results.append({
        "AIIB.No": "2.4",
        "Name": "Host should deactivate SNMP (Manual)",
        "CIS.No": "3.6",
        "CMD": None,
        "Host": None,
        "Value": None,
        "Description": "需要人工检查主机是否已停用 SNMP 服务",
        "Error": None
    })

    logger.info("检查 2.4: SNMP 手工检查，无法自动化，已输出提示")
    return results

def main():
    # 不依赖 VsphereConnection，因为这是手工检查
    snmp_info = get_hosts_snmp_manual()
    export_to_json(snmp_info, "../log/no_2.4_snmp_manual.json")

if __name__ == "__main__":
    main()
