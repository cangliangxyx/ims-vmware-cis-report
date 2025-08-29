import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def export_to_json(data: List[Dict[str, Any]], filename: str = "output.json") -> None:
    """导出数据到 JSON 文件"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info("数据已导出到: %s", filename)
    except Exception as e:
        logger.error("导出 JSON 失败: %s", e)
        raise
