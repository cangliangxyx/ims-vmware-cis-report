import logging
import yaml
import os
from typing import Callable, Tuple, Dict, Any, List

from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

# ------------------------------
# 导入检查模块
# ------------------------------
from vmware_cis_checks import (
    ntp_info,
    mem_share_salt,
    tsm_ssh,
    tsm,
    solo_enable_moob,
    snmp_manual,
    dcui_timeout,
    shell_warning_manual,
    password_complexity_manual,
    account_lock_failure,
    account_unlock_time,
    password_history_manual,
    password_max_days_manual,
    session_timeout_api_manual,
    idle_host_client_manual,
    dcui_access_manual,
    exception_users_manual,
    tls_version_manual,
    syslog_persistent_manual,
    syslog_remote_loghost,
    syslog_info_level_manual,
    log_filtering_manual,
    tls_log_verify_manual,
    firewall_services_manual,
    dvfilter_manual,
    bpdu_filter_manual,
    forged_transmits,
    mac_changes,
    vss_promiscuous_mode,
    vss_vlan_restrict,
    vss_vgt_check,
    management_network_manual,
)

# ------------------------------
# 日志配置
# ------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vmware_cis")

# ------------------------------
# 检查类型映射
# ------------------------------
CHECK_TYPE_MAPPING: Dict[str, Tuple[Callable[[Any], List[Dict[str, Any]]], str]] = {
    "ntp": (ntp_info.get_hosts_ntp, "ntp"),
    "advanced_setting": (mem_share_salt.get_hosts_mem_share_salt, "mem_share_salt"),
    "service_tsm_ssh": (tsm_ssh.get_hosts_ssh_service, "tsm_ssh"),
    "service_tsm": (tsm.get_hosts_tsm_service, "tsm"),
    "solo_enable_mob": (solo_enable_moob.get_hosts_solo_enable_mob, "solo_enable_mob"),
    "snmp_manual": (snmp_manual.get_hosts_snmp_manual, "snmp_manual"),
    "dcui_timeout": (dcui_timeout.get_hosts_dcui_timeout, "dcui_timeout"),
    "shell_warning_manual": (shell_warning_manual.get_hosts_shell_warning_manual, "shell_warning_manual"),
    "password_complexity_manual": (password_complexity_manual.get_hosts_password_complexity, "password_complexity_manual"),
    "account_lock_failure": (account_lock_failure.get_hosts_account_lock_failure, "account_lock_failure"),
    "account_unlock_time": (account_unlock_time.get_hosts_account_unlock_time, "account_unlock_time"),
    "password_history_manual": (password_history_manual.get_hosts_password_history, "password_history_manual"),
    "password_max_days_manual": (password_max_days_manual.get_hosts_password_max_days, "password_max_days_manual"),
    "session_timeout_api_manual": (session_timeout_api_manual.get_hosts_session_timeout_api, "session_timeout_api_manual"),
    "idle_host_client_manual": (idle_host_client_manual.get_hosts_idle_host_client_timeout, "idle_host_client_manual"),
    "dcui_access_manual": (dcui_access_manual.get_hosts_dcui_access, "dcui_access_manual"),
    "exception_users_manual": (exception_users_manual.get_hosts_exception_users, "exception_users_manual"),
    "tls_version_manual": (tls_version_manual.get_hosts_tls_version, "tls_version_manual"),
    "syslog_persistent_manual": (syslog_persistent_manual.get_hosts_syslog_persistent, "syslog_persistent_manual"),
    "syslog_remote_loghost": (syslog_remote_loghost.get_hosts_syslog_remote_loghost, "syslog_remote_loghost"),
    "syslog_info_level_manual": (syslog_info_level_manual.get_hosts_syslog_info_level, "syslog_info_level_manual"),
    "log_filtering_manual": (log_filtering_manual.get_hosts_log_filtering, "log_filtering_manual"),
    "tls_log_verify_manual": (tls_log_verify_manual.get_hosts_tls_log_verify, "tls_log_verify_manual"),
    "firewall_services_manual": (firewall_services_manual.get_hosts_firewall_services, "firewall_services_manual"),
    "dvfilter_manual": (dvfilter_manual.get_hosts_dvfilter, "dvfilter_manual"),
    "bpdu_filter_manual": (bpdu_filter_manual.get_hosts_bpdu_filter, "bpdu_filter_manual"),
    "forged_transmits": (forged_transmits.get_hosts_forged_transmits, "forged_transmits"),
    "mac_changes": (mac_changes.get_hosts_mac_changes, "mac_changes"),
    "vss_promiscuous_mode": (vss_promiscuous_mode.get_vss_security_policies, "vss_promiscuous_mode"),
    "vss_vlan_restrict": (vss_vlan_restrict.get_vss_portgroup_vlans, "vss_vlan_restrict"),
    "vss_vgt_check": (vss_vgt_check.get_vss_vgt_usage, "vss_vgt_check"),
    "management_network_manual": (management_network_manual.get_management_networks, "management_network_manual"),
}

# ------------------------------
# 辅助函数
# ------------------------------
def load_checks_config(path: str) -> List[Dict[str, Any]]:
    """从 YAML 文件加载检查配置"""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("checks", [])


def run_check(check: Dict[str, Any], content: Any, log_dir: str):
    """执行单个检查，导出 JSON 并记录日志"""
    check_id = check.get("id")
    check_type = check.get("type")
    if not check_type or check_type not in CHECK_TYPE_MAPPING:
        logger.warning("未知或未配置检查类型: %s", check_type)
        return

    func, file_suffix = CHECK_TYPE_MAPPING[check_type]
    logger.info("开始执行检查 %s: %s", check_id, check.get("name"))

    try:
        results = func(content)

        # 为每条记录补充 YAML 元数据
        for item in results:
            item.setdefault("NO", check_id)
            item.setdefault("name", check.get("name"))
            item.setdefault("CIS.NO", check.get("CIS.NO"))
            item.setdefault("cmd", check.get("cmd"))

        filename = os.path.join(log_dir, f"{check_id}_{file_suffix}.json")
        export_to_json(results, filename)
        logger.info("检查 %s 完成，结果导出到 %s", check_id, filename)

    except Exception as e:
        logger.exception("执行检查 %s 失败: %s", check_id, e)


# ------------------------------
# 主执行函数
# ------------------------------
def main():
    logger.info("========== VMware CIS Checks 开始 ==========")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(root_dir, "log")
    os.makedirs(log_dir, exist_ok=True)

    config_path = os.path.join(root_dir, "config", "vmware_cis_checks.yaml")
    checks_config = load_checks_config(config_path)
    if not checks_config:
        logger.warning("未加载到任何检查配置！")
        return

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        for check in checks_config:
            run_check(check, content, log_dir)

    logger.info("========== VMware CIS Checks 完成 ==========")


if __name__ == "__main__":
    main()
