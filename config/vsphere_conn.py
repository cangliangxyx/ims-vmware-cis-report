# config/vsphere_conn.py

import ssl
import os
import logging
from pyVim.connect import SmartConnect, Disconnect
from config import settings


# === 配置日志 ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class VsphereConnection:
    """vSphere 连接的上下文管理器"""

    def __init__(self, env: str = "prod"):
        self.env = env
        self.service_instance = None

    def __enter__(self):
        vsphere_data = settings.get_vsphere_config(os.getenv("project_env", self.env))
        host = vsphere_data["HOST"]
        username = vsphere_data["USERNAME"]
        password = vsphere_data["PASSWORD"]

        context = ssl._create_unverified_context()
        self.service_instance = SmartConnect(
            host=host, user=username, pwd=password, sslContext=context
        )
        logger.info("成功连接 vSphere: %s", host)
        return self.service_instance

    def __exit__(self, exc_type, exc_value, traceback):
        if self.service_instance:
            Disconnect(self.service_instance)
            logger.info("已断开 vSphere 连接")
