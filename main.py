import logging
import yaml
import os

from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

from vmware_cis_checks import ntp_info as ntp
from vmware_cis_checks import mem_share_salt as mem_salt
from vmware_cis_checks import tsm_ssh as tsm_ssh
from vmware_cis_checks import tsm as tsm
from vmware_cis_checks import solo_enable_moob as solo
from vmware_cis_checks import snmp_manual as snmp
from vmware_cis_checks import dcui_timeout as dcui
from vmware_cis_checks import shell_warning_manual as shell_warning
from vmware_cis_checks import password_complexity_manual as password_complexity
from vmware_cis_checks import account_lock_failure as lock_failure
from vmware_cis_checks import account_unlock_time as unlock_time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 存储 (函数, 文件名后缀)
CHECK_TYPE_MAPPING = {
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


def main():
    # 根目录和 log 目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(root_dir, "log")
    os.makedirs(log_dir, exist_ok=True)

    # 读取配置
    with open(os.path.join(root_dir, "config", "vmware_cis_checks.yaml"), "r", encoding="utf-8") as f:
        checks_config = yaml.safe_load(f)

    # 连接 vSphere
    with VsphereConnection() as si:
        content = si.RetrieveContent()

        for check in checks_config["checks"]:
            check_type = check["type"]

            if check_type in CHECK_TYPE_MAPPING:
                func, suffix = CHECK_TYPE_MAPPING[check_type]
                # 手工检查也统一调用
                result = func(content)
            else:
                logger.warning("未知检查类型: %s", check_type)
                continue

            # 文件名加后缀：例如 no_1.2_ntp.json
            filename = os.path.join(log_dir, f"{check['id']}_{suffix}.json")
            export_to_json(result, filename)
            logger.info("检查 %s 完成，导出到 %s", check['id'], filename)


if __name__ == "__main__":
    main()
