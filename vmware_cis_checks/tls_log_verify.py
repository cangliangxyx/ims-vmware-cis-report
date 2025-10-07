import os
import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def collect_tls_log_verify(content) -> List[Dict[str, Any]]:
    """
    检查是否启用了远程日志 TLS 证书验证 (Syslog.global.certificate.checkSSLCerts)
    推荐值：True（开启证书验证，保证日志目标可信）
    """
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view
    results: List[Dict[str, Any]] = []

    for host in hosts:
        try:
            adv_settings = host.configManager.advancedOption.QueryOptions("Syslog.global.certificate.checkSSLCerts")

            if adv_settings:
                setting = adv_settings[0]
                value = str(setting.value).strip() if setting.value is not None else ""
                value_lower = value.lower()

                # 判断状态
                status = "Pass" if value_lower == "true" else "Fail"

                results.append({
                    "AIIB.No": "3.5",
                    "Name": "Host must verify certificates for TLS remote logging endpoints",
                    "CIS.No": "4.10",
                    "CMD": "host -> configure -> advanced system setting -> Syslog.global.certificate.checkSSLCerts",
                    "Host": host.name,
                    "Value": value,
                    "Status": status,
                    "Description": (
                        f"检测值: Syslog.global.certificate.checkSSLCerts = '{value or '未配置'}' | "
                        "推荐值: 'True' (启用 TLS 证书验证以确保日志端点可信)"
                    ),
                    "Error": None
                })

                logger.info("[TLS Verify] 主机: %s | 值: %s | 状态: %s", host.name, value or "未配置", status)

            else:
                # 未配置的情况
                results.append({
                    "AIIB.No": "3.5",
                    "Name": "Host must verify certificates for TLS remote logging endpoints",
                    "CIS.No": "4.10",
                    "CMD": "host -> configure -> advanced system setting -> Syslog.global.certificate.checkSSLCerts",
                    "Host": host.name,
                    "Value": None,
                    "Status": "Fail",
                    "Description": "未配置 Syslog.global.certificate.checkSSLCerts，建议显式设置为 True。",
                    "Error": None
                })
                logger.warning("[TLS Verify] 主机 %s 未配置 Syslog.global.certificate.checkSSLCerts", host.name)

        except vim.fault.InvalidName as e:
            results.append({
                "AIIB.No": "3.5",
                "Name": "Host must verify certificates for TLS remote logging endpoints",
                "CIS.No": "4.10",
                "CMD": "host -> configure -> advanced system setting -> Syslog.global.certificate.checkSSLCerts",
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "该主机不支持 Syslog.global.certificate.checkSSLCerts 配置项。",
                "Error": str(e)
            })
            logger.info("[TLS Verify] 主机 %s 不支持 Syslog.global.certificate.checkSSLCerts 设置", host.name)

        except Exception as e:
            results.append({
                "AIIB.No": "3.5",
                "Name": "Host must verify certificates for TLS remote logging endpoints",
                "CIS.No": "4.10",
                "CMD": "host -> configure -> advanced system setting -> Syslog.global.certificate.checkSSLCerts",
                "Host": host.name,
                "Value": None,
                "Status": "Fail",
                "Description": "获取 Syslog.global.certificate.checkSSLCerts 失败。",
                "Error": str(e)
            })
            logger.error("[TLS Verify] 主机 %s 获取 Syslog.global.certificate.checkSSLCerts 失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    """
    循环多个 vCenter，检查所有主机的 TLS 日志证书验证配置，并导出为 JSON。
    """
    output_dir = output_dir or "../log"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "no_3.5_tls_log_verify.json")

    # 获取 vCenter 列表
    vsphere_data = settings.get_vsphere_config(os.getenv('project_env', 'prod'))
    vc_list = vsphere_data.get("HOST", [])
    if not isinstance(vc_list, list):
        vc_list = [vc_list]

    all_results: List[Dict[str, Any]] = []

    for vc_host in vc_list:
        try:
            logger.info("[TLS Verify] 正在连接 vCenter: %s", vc_host)
            with VsphereConnection(host=vc_host) as si:
                content = si.RetrieveContent()
                results = collect_tls_log_verify(content)
                all_results.extend(results)
        except Exception as e:
            logger.error("[TLS Verify] 无法连接 vCenter %s: %s", vc_host, e)

    export_to_json(all_results, output_path)
    logger.info("[TLS Verify] 所有主机 Syslog.global.certificate.checkSSLCerts 检查结果已导出到 %s", output_path)


if __name__ == "__main__":
    main()
