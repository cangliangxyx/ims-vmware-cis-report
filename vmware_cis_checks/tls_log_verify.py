import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_hosts_tls_log_verify(content) -> List[Dict[str, Any]]:
    """
    检查是否启用了远程日志 TLS 证书验证 (Syslog.global.certificate.checkSSLCerts)
    推荐值：True（开启证书验证，保证日志目标可信）
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.certificate.checkSSLCerts")
            if adv_settings:
                setting = adv_settings[0]
                raw_value = {
                    "key": setting.key,
                    "value": setting.value,
                    "type": type(setting.value).__name__
                }
                results.append({
                    "AIIB.No": "3.5",
                    "Name": "Syslog.global.certificate.checkSSLCerts (Read Only)",
                    "CIS.No": "4.10",
                    "CMD": "host-->configure->advanced system setting --> Syslog.global.certificate.checkSSLCerts",
                    "Host": host.name,
                    "Value": raw_value,
                    "Description": f"检测值:启用 TLS 证书验证，检测方法：'value': 'True'",
                    "Error": None
                })
                logger.info("主机 %s Syslog.global.certificate.checkSSLCerts = %s", host.name, setting.value)
            else:
                results.append({
                    "AIIB.No": "3.5",
                    "Name": "Syslog.global.certificate.checkSSLCerts (Read Only)",
                    "CIS.No": "4.10",
                    "CMD": "host-->configure->advanced system setting --> Syslog.global.certificate.checkSSLCerts",
                    "Host": host.name,
                    "Value": {"key": "Syslog.global.certificate.checkSSLCerts", "value": None, "type": None},
                    "Description": "未配置 Syslog.global.certificate.checkSSLCerts，建议显式设置为 True。",
                    "Error": None
                })
                logger.warning("主机 %s 未配置 Syslog.global.certificate.checkSSLCerts", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.5",
                "Name": "Syslog.global.certificate.checkSSLCerts (Read Only)",
                "CIS.No": "4.10",
                "CMD": "host-->configure->advanced system setting --> Syslog.global.certificate.checkSSLCerts",
                "Host": host.name,
                "Value": None,
                "Description": "该主机不支持 Syslog.global.certificate.checkSSLCerts 设置",
                "Error": str(e)
            })
            logger.info("主机 %s 不支持 Syslog.global.certificate.checkSSLCerts 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "3.5",
                "Name": "Syslog.global.certificate.checkSSLCerts (Read Only)",
                "CIS.No": "4.10",
                "CMD": "host-->configure->advanced system setting --> Syslog.global.certificate.checkSSLCerts",
                "Host": host.name,
                "Value": None,
                "Description": "查询 Syslog.global.certificate.checkSSLCerts 失败",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 Syslog.global.certificate.checkSSLCerts 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    检查主机 TLS 日志证书验证是否启用，并导出 JSON。
    :param output_dir: 输出目录路径（默认 ../log）
    """
    output_dir = output_dir or "../log"
    output_path = f"{output_dir}/no_3.5_tls_log_verify.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        tls_log_info = get_hosts_tls_log_verify(content)
        export_to_json(tls_log_info, output_path)
        logger.info("Syslog.global.certificate.checkSSLCerts 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
