import logging
import importlib
import os

from vmware_cis_checks import (
    ntp_info, # ok
    mem_share_salt, # ok
    tsm_ssh,    # ok
    tsm,    # ok
    solo_enable_moob,   # ok
    snmp_manual,   # ok
    dcui_timeout,   # ok
    shell_warning_manual,   # ok
    password_complexity_manual, # ok
    account_lock_failure, # 修改完成，取值错误，需要再次排查
    account_unlock_time,  # ok
    password_history_manual,    # ok
    password_max_days_manual,    # ok
    session_timeout_api_manual, # ok
    idle_host_client_manual,    #ok
    dcui_access, # ok
    exception_users_manual, # ok
    tls_version_manual, # ok
    syslog_persistent,  # ok
    syslog_remote_loghost, # ok
    syslog_info_level_manual, # ok
    log_filtering_manual,   # ok
    tls_log_verify_manual,  # ok
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
# 配置日志
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ------------------------------
# 项目根目录 & 日志输出路径
# ------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_ROOT, "log")
os.makedirs(LOG_DIR, exist_ok=True)  # 确保 log/ 存在

# ------------------------------
# 要执行的检查模块
# ------------------------------
CHECK_MODULES = [
    "vmware_cis_checks.ntp_info",
    "vmware_cis_checks.mem_share_salt",
    "vmware_cis_checks.tsm_ssh",
    "vmware_cis_checks.tsm",
    "vmware_cis_checks.solo_enable_moob",
    "vmware_cis_checks.snmp_manual",
    "vmware_cis_checks.dcui_timeout",
    "vmware_cis_checks.shell_warning_manual",
    "vmware_cis_checks.password_complexity_manual",
    "vmware_cis_checks.account_lock_failure",
    "vmware_cis_checks.account_unlock_time",
    "vmware_cis_checks.password_history_manual",
    "vmware_cis_checks.password_max_days_manual",
    "vmware_cis_checks.session_timeout_api_manual",
    "vmware_cis_checks.idle_host_client_manual",
    "vmware_cis_checks.dcui_access",
    "vmware_cis_checks.exception_users_manual",
    "vmware_cis_checks.tls_version_manual",
    "vmware_cis_checks.syslog_persistent",
    "vmware_cis_checks.syslog_remote_loghost",
    "vmware_cis_checks.syslog_info_level_manual",
    "vmware_cis_checks.log_filtering_manual",
    "vmware_cis_checks.tls_log_verify_manual",
    "vmware_cis_checks.firewall_services_manual",
    "vmware_cis_checks.dvfilter_manual",
    "vmware_cis_checks.bpdu_filter_manual",
    "vmware_cis_checks.forged_transmits",
    "vmware_cis_checks.mac_changes",
    "vmware_cis_checks.vss_promiscuous_mode",
    "vmware_cis_checks.vss_vlan_restrict",
    "vmware_cis_checks.vss_vgt_check",
    "vmware_cis_checks.management_network_manual"
]

def main():
    for module_name in CHECK_MODULES:
        try:
            logger.info("执行模块: %s", module_name)
            module = importlib.import_module(module_name)
            if hasattr(module, "main"):
                module.main(LOG_DIR)  # 把日志目录作为参数传进去
            else:
                logger.warning("模块 %s 没有 main() 方法，跳过", module_name)
        except Exception as e:
            logger.error("模块 %s 执行失败: %s", module_name, e)

if __name__ == "__main__":
    main()
