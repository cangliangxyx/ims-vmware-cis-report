import logging
import importlib
import os

from vmware_cis_checks import (
    ntp_info,  # no_1.2
    mem_share_salt,  # no_1.4
    tsm_ssh,  # no_2.1
    tsm,  # no_2.2
    solo_enable_moob,  # no_2.3
    snmp_manual,  # no_2.4
    dcui_timeout,  # no_2.5
    shell_warning_manual,  # no_2.6
    password_complexity_manual,  # no_2.7
    account_lock_failure,  # no_2.8
    account_unlock_time,  # no_2.9
    password_history_manual,  # no_2.10
    password_max_days_manual,  # no_2.11
    session_timeout_api_manual,  # no_2.12
    idle_host_client_manual,  # no_2.13
    dcui_access,  # no_2.14
    exception_users_manual,  # no_2.15
    tls_version_manual,  # no_2.16
    syslog_persistent,  # no_3.1
    syslog_remote_loghost,  # no_3.2
    hostagent_log_level,  # no_3.3
    log_filtering,  # no_3.4
    tls_log_verify,  # no_3.5
    firewall_services_manual,  # no_4.1
    dvfilter_manual,  # no_4.2
    bpdu_filter_manual,  # no_4.3
    forged_transmits,  # no_4.4
    mac_changes,  # no_4.5
    vss_promiscuous_mode,  # no_4.6
    vss_vlan_restrict,  # no_4.7
    vss_vgt_check,  # no_4.8
    management_network_manual,  # no_4.9
    datastore_unique_names,  # no_5.1
    vm_3d_graphics_status,  # no_6.1
    vm_pci_passthru,  # no_6.2
    vm_audio_device_manual,  # no_6.3
    vm_ahci_device_manual,  # no_6.4
    vm_usb_settings,  # no_6.5
    vm_serial_port,  # no_6.6
    vm_parallel_port,  # no_6.7
    vm_cd_drive,  # no_6.8
    vm_floppy_drive,  # no_6.9
    vm_hardware_version_manual,  # no_6.10
    vmware_tools_update_manual,  # no_7.1
    vmware_tools_auto_upgrade_manual,  # no_7.2
    vmware_tools_prevent_recustomization_manual  # no_7.3
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
# 要执行的检查模块 (顺序与 import 顺序一致)
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
    "vmware_cis_checks.hostagent_log_level",
    "vmware_cis_checks.log_filtering",
    "vmware_cis_checks.tls_log_verify",
    "vmware_cis_checks.firewall_services_manual",
    "vmware_cis_checks.dvfilter_manual",
    "vmware_cis_checks.bpdu_filter_manual",
    "vmware_cis_checks.forged_transmits",
    "vmware_cis_checks.mac_changes",
    "vmware_cis_checks.vss_promiscuous_mode",
    "vmware_cis_checks.vss_vlan_restrict",
    "vmware_cis_checks.vss_vgt_check",
    "vmware_cis_checks.management_network_manual",
    "vmware_cis_checks.datastore_unique_names",
    "vmware_cis_checks.vm_3d_graphics_status",  # 6.1
    "vmware_cis_checks.vm_pci_passthru",  # 6.2
    "vmware_cis_checks.vm_audio_device_manual",  # 6.3
    "vmware_cis_checks.vm_ahci_device_manual",  # 6.4
    "vmware_cis_checks.vm_usb_settings",  # 6.5
    "vmware_cis_checks.vm_serial_port",  # 6.6
    "vmware_cis_checks.vm_parallel_port",  # 6.7
    "vmware_cis_checks.vm_cd_drive",  # 6.8
    "vmware_cis_checks.vm_floppy_drive",  # 6.9
    "vmware_cis_checks.vm_hardware_version_manual",  # 6.10
    "vmware_cis_checks.vmware_tools_update_manual", # 7.1
    "vmware_cis_checks.vmware_tools_auto_upgrade_manual", # 7.2
    "vmware_cis_checks.vmware_tools_prevent_recustomization_manual" # 7.3
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
