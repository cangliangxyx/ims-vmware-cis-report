# config/vsphere_conn.py

import ssl
import os
import logging
from pyVim.connect import SmartConnect, Disconnect
from config import settings
from pyVmomi import vim

# === 配置日志 ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class VsphereConnection:
    """vSphere 连接的上下文管理器，可接受 host 参数"""

    def __init__(self, host: str = None, env: str = "prod"):
        self.env = env
        self.host = host
        self.service_instance = None

    def __enter__(self):
        vsphere_data = settings.get_vsphere_config(os.getenv("project_env", self.env))
        username = vsphere_data["USERNAME"]
        password = vsphere_data["PASSWORD"]

        if not self.host:
            host_config = vsphere_data["HOST"]
            if isinstance(host_config, list):
                self.host = host_config[0]
            else:
                self.host = host_config

        context = ssl._create_unverified_context()
        self.service_instance = SmartConnect(
            host=self.host, user=username, pwd=password, sslContext=context
        )
        logger.info("成功连接 vSphere: %s", self.host)
        return self.service_instance

    def __exit__(self, exc_type, exc_value, traceback):
        if self.service_instance:
            Disconnect(self.service_instance)
            logger.info("已断开 vSphere 连接")

    def get_all_hosts_name(env: str = "prod") -> list[str]:
        """
        循环多个 vCenter，返回所有 ESXi 主机名的列表
        """
        vsphere_data = settings.get_vsphere_config(os.getenv('project_env', env))
        host_list = vsphere_data.get("HOST")
        if not isinstance(host_list, list):
            host_list = [host_list]

        all_hosts = []

        for vc_host in host_list:
            try:
                with VsphereConnection(host=vc_host) as si:
                    hosts = si.get_all_host_names()  # 调用你之前写的 VsphereConnection 方法
                    all_hosts.extend(hosts)
            except Exception as e:
                logger.error("连接 vCenter %s 失败: %s", vc_host, e)

        return all_hosts

# === 测试 main 方法 ===
if __name__ == "__main__":
    # 从 settings 获取 host 列表
    vsphere_data = settings.get_vsphere_config("prod")
    hosts = vsphere_data.get("HOST")
    if not isinstance(hosts, list):
        hosts = [hosts]

    for host in hosts:
        logger.info("开始连接 vCenter: %s", host)
        try:
            with VsphereConnection(host=host) as si:
                content = si.RetrieveContent()
                logger.info("成功获取 %s 的 content", host)
        except Exception as e:
            logger.error("连接 vCenter %s 失败: %s", host, e)
