import logging
import yaml
import os
from typing import Callable, Tuple, Dict, Any, List

from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

from vmware_cis_checks import (
    ntp_info as ntp,
    mem_share_salt as mem_salt,
    tsm_ssh as tsm_ssh,
    tsm as tsm,
    solo_enable_moob as solo,
    snmp_manual as snmp,
    dcui_timeout as dcui,
    shell_warning_manual as shell_warning,
    password_complexity_manual as password_complexity,
    account_lock_failure as lock_failure,
    account_unlock_time as unlock_time,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vmware_cis")

# v1.0.3 新增检查只需更新 YAML + 注册函数，无需改 main.py

# ------------------------------
# 配置检查映射
# ------------------------------
CHECK_TYPE_MAPPING: Dict[str, Tuple[Callable[[Any], List[Dict[str, Any]]], str]] = {
    "ntp": (ntp.get_hosts_ntp, "ntp"),
    "advanced_setting": (mem_salt.get_hosts_mem_share_salt, "mem_share_salt"),
    "service_tsm_ssh": (tsm_ssh.get_hosts_ssh_service, "tsm_ssh"),
    "service_tsm": (tsm.get_hosts_tsm_service, "tsm"),
    "solo_enable_mob": (solo.get_hosts_solo_enable_mob, "solo_enable_mob"),
    "snmp_manual": (snmp.get_hosts_snmp_manual, "snmp_manual"),
    "dcui_timeout": (dcui.get_hosts_dcui_timeout, "dcui_timeout"),
    "shell_warning_manual": (shell_warning.get_hosts_shell_warning_manual, "shell_warning_manual"),
    "password_complexity_manual": (password_complexity.get_hosts_password_complexity, "password_complexity_manual"),
    "account_lock_failure": (lock_failure.get_hosts_account_lock_failure, "account_lock_failure"),
    "account_unlock_time": (unlock_time.get_hosts_account_unlock_time, "account_unlock_time"),
}


# ------------------------------
# 辅助函数
# ------------------------------
def load_checks_config(path: str) -> List[Dict[str, Any]]:
    """从 YAML 文件加载检查配置"""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("checks", [])


def run_check(
    check: Dict[str, Any],
    content: Any,
    log_dir: str
):
    """执行单个检查，导出 JSON 并记录日志"""
    check_id = check["id"]
    check_type = check["type"]

    if check_type not in CHECK_TYPE_MAPPING:
        logger.warning("未知检查类型: %s", check_type)
        return

    func, file_suffix = CHECK_TYPE_MAPPING[check_type]
    try:
        results = func(content)

        # 为每条记录补充 YAML 元数据
        for item in results:
            item.setdefault("NO", check.get("id"))
            item.setdefault("name", check.get("name"))
            item.setdefault("CIS.NO", check.get("CIS.NO"))
            item.setdefault("cmd", check.get("cmd"))

        filename = os.path.join(log_dir, f"{check_id}_{file_suffix}.json")
        export_to_json(results, filename)
        logger.info("检查 %s 完成，导出到 %s", check_id, filename)
    except Exception as e:
        logger.error("检查 %s 执行失败: %s", check_id, e)


# ------------------------------
# 主执行函数
# ------------------------------
def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(root_dir, "log")
    os.makedirs(log_dir, exist_ok=True)

    checks_config = load_checks_config(os.path.join(root_dir, "config", "vmware_cis_checks.yaml"))

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        for check in checks_config:
            run_check(check, content, log_dir)


if __name__ == "__main__":
    main()
