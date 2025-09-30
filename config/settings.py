# settings.py
import os
import platform
from config.decrypt_message import decrypt_message

# MySQL 数据库配置
DATABASE_CONFIG = {
    "test":{
    'host': '10.33.16.33',
    'port': 3306,
    'user': 'dbta_db_cmdbapp',
    'password': decrypt_message('gAAAAABoJX0z4UP7xK9xicG7uXGurTI7PVJ9qDrnbHqokEK_62m8wk3b-OWwGWQ1CcOJxK2xPjR0reRL9T5XWORgJrwz9Eb_E_VTEv8ebFcpGh33USQ7uro='),
    'database': 'auto_cmdb',
    'charset': 'utf8mb4'
    },
    "prod":{
    'host': '10.36.24.253',
    'port': 3306,
    'user': 'dbpa_elp_autocmdb',
    'password': decrypt_message('gAAAAABoJX0Y_pKkcjbZ1zaSUqCdRRgrk7WbLz-s3dL4KZ2PLU0Xrhwkl_-2DrDHC9Gy18dEnk3nX0ItOOyA8NH2DcpV6Adaug=='),
    'database': 'auto_cmdb',
    'charset': 'utf8mb4'
    }
}

# vsphere 配置
VSPHERE_CONFIG = {
    "prod": {
        "HOST":["vc-bj-01.vsphere.aiib.org", "vc-tj-01.vsphere.aiib.org"],
        "USERNAME":"psa-infra-pbi@aiib.org",
        "PASSWORD":decrypt_message("gAAAAABoJX45Du7Y4pvoMLqiIxX1UEDSYpSwCuLmfu7ZQMG1XEnNhLDRf-_LzvtdFDuYzHhEsfdwwfqt7UGSR53wdQTWtFq1NgtouVhFiaFcHx2VqcXjR3Q="),
        "ENDPOINT":"/rest/com/vmware/cis/session"
    },
    "test":{
        "HOST":"vc01.vsphere.aiib.local",
        "USERNAME":"cmdreader@vsphere.local",
        "PASSWORD":decrypt_message("gAAAAABoJX5bmyY36zCdWf51Ekp83476X1EZmIZO-nS3NbUVhd3zpHJhl-ARa2o1iz_rOHHDf0u6CeZrUOR05S7GFqblpKDfmg=="),
        "ENDPOINT":"/rest/com/vmware/cis/session"
    }
}

def get_vsphere_config(env):
    """ 根据环境 env 获取 vsphere 配置信息 """
    return VSPHERE_CONFIG[env]

def get_database_config(env):
    """ 根据环境 env 获取 vsphere 配置信息 """
    return DATABASE_CONFIG[env]

if __name__ == "__main__":
    project_env = os.getenv('project_env', 'prod')  # 如果没有设置，则默认为 prod
    print(f"Current Project Environment: {project_env}")

    vsphere_data = get_vsphere_config(project_env)
    print("Vsphere Config:", vsphere_data)

    db_config = get_database_config(project_env)
    print("Database Config:", db_config)

