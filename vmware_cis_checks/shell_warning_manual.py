import logging
from typing import List, Dict, Any
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_hosts_shell_warning_manual(content=None) -> List[Dict[str, Any]]:
    """
    手工检查：Host must not suppress warnings that the shell is enabled
    """
    results = []

    results.append({
        "AIIB.No": "2.6",
        "Name": "Host must not suppress warnings that the shell is enabled (Manual)",
        "CIS.No": "3.10",
        "CMD": None,
        "Host": None,
        "Value": None,
        "Description": "需要人工检查主机是否未抑制 shell 启用警告",
        "Error": None
    })

    logger.info("检查 2.6: shell warning 手工检查，无法自动化，已生成提示")
    return results

def main(output_dir: str = None):
    """
    手工检查 Shell Warning 并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    # 如果没有传 output_dir，就用默认目录 ../log
    if output_dir is None:
        output_dir = "../log"

    # 拼接输出文件路径
    output_path = f"{output_dir}/no_2.6_shell_warning_manual.json"

    # 获取数据并导出
    shell_warning_info = get_hosts_shell_warning_manual()
    export_to_json(shell_warning_info, output_path)


if __name__ == "__main__":
    main()
