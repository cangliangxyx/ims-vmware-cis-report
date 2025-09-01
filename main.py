# main.py

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
    password_history_manual as password_history,
    password_max_days_manual as password_max_days,
    session_timeout_api_manual as session_timeout_api,   # 新增 2.12
    idle_host_client_manual as idle_host_client,         # 新增 2.13
    dcui_access_manual as dcui_access,                   # 新增 2.14
    exception_users_manual as exception_users,           # 新增 2.15
    tls_version_manual as tls_version,                   # 新增 2.16
    syslog_persistent_manual as syslog_persistent,       # 新增 3.1
    syslog_remote_loghost as syslog_remote,              # 新增 3.2
    syslog_info_level_manual as syslog_info_level,       # 新增 3.3
    log_filtering_manual as log_filtering,               # 新增 3.4
    tls_log_verify_manual as tls_log_verify,             # 新增 3.5
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
    "password_history_manual": (password_history.get_hosts_password_history, "password_history_manual"),
    "password_max_days_manual": (password_max_days.get_hosts_password_max_days, "password_max_days_manual"),
    "session_timeout_api_manual": (session_timeout_api.get_hosts_session_timeout_api, "session_timeout_api_manual"),
    "idle_host_client_manual": (idle_host_client.get_hosts_idle_host_client_timeout, "idle_host_client_manual"),
    "dcui_access_manual": (dcui_access.get_hosts_dcui_access, "dcui_access_manual"),
    "exception_users_manual": (exception_users.get_hosts_exception_users, "exception_users_manual"),
    "tls_version_manual": (tls_version.get_hosts_tls_version, "tls_version_manual"),
    "syslog_persistent_manual": (syslog_persistent.get_hosts_syslog_persistent, "syslog_persistent_manual"),
    "syslog_remote_loghost": (syslog_remote.get_hosts_syslog_remote_loghost, "syslog_remote_loghost"),
    "syslog_info_level_manual": (syslog_info_level.get_hosts_syslog_info_level, "syslog_info_level_manual"),
    "log_filtering_manual": (log_filtering.get_hosts_log_filtering, "log_filtering_manual"),
    "tls_log_verify_manual": (tls_log_verify.get_hosts_tls_log_verify, "tls_log_verify_manual"),
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
