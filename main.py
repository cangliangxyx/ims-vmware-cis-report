import logging
import yaml
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

from vmware_cis_checks import ntp_info as ntp
from vmware_cis_checks import mem_share_salt as mem_salt
from vmware_cis_checks import tsm_ssh as tsm_ssh
from vmware_cis_checks import tsm as tsm
from vmware_cis_checks import solo_enable_moob as solo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CHECK_TYPE_MAPPING = {
    "ntp": ntp.get_hosts_ntp,
    "advanced_setting": mem_salt.get_hosts_mem_share_salt,
    "service_tsm_ssh": tsm_ssh.get_hosts_ssh_service,
    "service_tsm": tsm.get_hosts_tsm_service,
    "solo_enable_mob": solo.get_hosts_solo_enable_mob,
}

def main():
    with open("config/vmware_cis_checks.yaml", "r", encoding="utf-8") as f:
        checks_config = yaml.safe_load(f)

    with VsphereConnection() as si:
        content = si.RetrieveContent()

        for check in checks_config["checks"]:
            check_type = check["type"]
            key = check.get("key")

            if check_type == "ntp":
                result = CHECK_TYPE_MAPPING[check_type](content)
            elif check_type == "advanced_setting":
                result = CHECK_TYPE_MAPPING[check_type](content, key)
            elif check_type.startswith("service"):
                result = CHECK_TYPE_MAPPING[check_type](content, key)
            else:
                logger.warning("未知检查类型: %s", check_type)
                continue

            filename = f"{check['id']}.json"
            export_to_json(result, filename)
            logger.info("检查 %s 完成，导出到 %s", check['id'], filename)


if __name__ == "__main__":
    main()
