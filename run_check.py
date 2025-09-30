# 导入模块并标注检查编号
from vmware_cis_checks import (
    software_general,                     # 1.1
    ntp_info,                             # 1.2
    time_sync,                            # 1.3
    mem_share_salt,                       # 1.4
    tsm_ssh,                              # 2.1
    tsm,                                  # 2.2
    solo_enable_moob,                     # 2.3
    snmp_manual,                           # 2.4
    dcui_timeout,                          # 2.5
    shell_warning_manual,                  # 2.6
    password_complexity_manual,            # 2.7
    account_lock_failure,                  # 2.8
    account_unlock_time,                   # 2.9
    password_history_manual,               # 2.10
    password_max_days_manual,              # 2.11
    session_timeout_api_manual,            # 2.12
    idle_host_client_manual,               # 2.13
    dcui_access,                           # 2.14
    exception_users_manual,                # 2.15
    tls_version_manual,                    # 2.16
    syslog_persistent,                     # 3.1
    syslog_remote_loghost,                 # 3.2
    hostagent_log_level,                   # 3.3
    log_filtering,                         # 3.4
    tls_log_verify,                        # 3.5
    firewall_services_manual,              # 4.1
    dvfilter_manual,                       # 4.2
    bpdu_filter,                           # 4.3
    forged_transmits,                      # 4.4
    mac_changes,                           # 4.5
    vss_promiscuous_mode,                  # 4.6
    vss_vlan_restrict,                     # 4.7
    vss_vgt_check,                         # 4.8
    management_network_manual,             # 4.9
    datastore_unique_names,                # 5.1
    vm_3d_graphics_status,                 # 6.1
    vm_pci_passthru,                       # 6.2
    vm_audio_device_manual,                 # 6.3
    vm_ahci_device_manual,                  # 6.4
    vm_usb_settings,                        # 6.5
    vm_serial_port,                         # 6.6
    vm_parallel_port,                       # 6.7
    vm_cd_drive,                            # 6.8
    vm_floppy_drive,                        # 6.9
    vm_hardware_version_manual,             # 6.10
    vmware_tools_update_manual,             # 7.1
    vmware_tools_auto_upgrade_manual,       # 7.2
    vmware_tools_prevent_recustomization_manual  # 7.3
)

# 将模块和编号整合成统一列表，方便循环执行
check_modules = [
    ("1.1", software_general),
    ("1.2", ntp_info),
    ("1.3", time_sync),
    ("1.4", mem_share_salt),
    ("2.1", tsm_ssh),
    ("2.2", tsm),
    ("2.3", solo_enable_moob),
    ("2.4", snmp_manual),
    ("2.5", dcui_timeout),
    ("2.6", shell_warning_manual),
    ("2.7", password_complexity_manual),
    ("2.8", account_lock_failure),
    ("2.9", account_unlock_time),
    ("2.10", password_history_manual),
    ("2.11", password_max_days_manual),
    ("2.12", session_timeout_api_manual),
    ("2.13", idle_host_client_manual),
    ("2.14", dcui_access),
    ("2.15", exception_users_manual),
    ("2.16", tls_version_manual),
    ("3.1", syslog_persistent),
    ("3.2", syslog_remote_loghost),
    ("3.3", hostagent_log_level),
    ("3.4", log_filtering),
    ("3.5", tls_log_verify),
    ("4.1", firewall_services_manual),
    ("4.2", dvfilter_manual),
    ("4.3", bpdu_filter),
    ("4.4", forged_transmits),
    ("4.5", mac_changes),
    ("4.6", vss_promiscuous_mode),
    ("4.7", vss_vlan_restrict),
    ("4.8", vss_vgt_check),
    ("4.9", management_network_manual),
    ("5.1", datastore_unique_names),
    ("6.1", vm_3d_graphics_status),
    ("6.2", vm_pci_passthru),
    ("6.3", vm_audio_device_manual),
    ("6.4", vm_ahci_device_manual),
    ("6.5", vm_usb_settings),
    ("6.6", vm_serial_port),
    ("6.7", vm_parallel_port),
    ("6.8", vm_cd_drive),
    ("6.9", vm_floppy_drive),
    ("6.10", vm_hardware_version_manual),
    ("7.1", vmware_tools_update_manual),
    ("7.2", vmware_tools_auto_upgrade_manual),
    ("7.3", vmware_tools_prevent_recustomization_manual)
]

import os
from config import settings
from config.export_to_json import export_to_json
from config.vsphere_conn import VsphereConnection
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

output_dir = "log"
os.makedirs(output_dir, exist_ok=True)

def run_check():
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    host_list = vsphere_data["HOST"]
    if not isinstance(host_list, list):
        host_list = [host_list]

    # 循环所有 vCenter
    for vc_host in host_list:
        try:
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                # 循环所有模块
                for aiib_no, module in check_modules:
                    try:
                        logger.info("执行检查 %s -> %s", aiib_no, module.__name__)
                        result_list = module.get_hosts_ntp(content) if hasattr(module, "get_hosts_ntp") else module.main()  # 根据模块类型调用
                        # 按主机拆分存文件
                        for entry in result_list:
                            hostname = entry.get("Host", "unknown")
                            file_path = os.path.join(output_dir, f"{aiib_no}_{hostname}.json")
                            export_to_json([entry], file_path)
                            logger.info("主机 %s 的 %s 检查结果已导出到 %s", hostname, aiib_no, file_path)
                    except Exception as e:
                        logger.error("执行模块 %s 失败: %s", module.__name__, e)

        except Exception as e:
            logger.error("连接 vCenter %s 失败: %s", vc_host, e)

# 示例统一 main 调用
if __name__ == "__main__":
    run_check()
