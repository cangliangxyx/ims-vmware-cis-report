import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_hosts_password_complexity(content=None) -> List[Dict[str, Any]]:
    """
    检查：Host must enforce password complexity (Manual/Automated)
    """
    results = []

    results.append({
        "AIIB.No": "2.7",
        "Name": "Host must enforce password complexity (Manual)",
        "CIS.No": "3.11",
        "CMD": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select VMHost, Key, Label, Policy, Running, Required',
        "Host": None,
        "Value": None,
        "Description": "需要人工或脚本验证密码复杂性策略",
        "Error": None
    })

    logger.info("检查 2.7: 密码复杂性检查，生成提示")
    return results

def main(output_dir: str = None):
    """
    手工检查密码复杂度配置并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_2.7_password_complexity_manual.json"

    # 获取数据并导出
    password_info = get_hosts_password_complexity()
    export_to_json(password_info, output_path)

if __name__ == "__main__":
    main()
