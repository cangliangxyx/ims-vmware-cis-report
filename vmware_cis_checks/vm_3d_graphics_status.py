import logging
from typing import List, Dict, Any
from pyVmomi import vim
from config.vsphere_conn import VsphereConnection
from config.export_to_json import export_to_json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_hosts_vm_3d_settings(content) -> List[Dict[str, Any]]:
    """获取所有主机下 VM 的 mks.enable3d 配置"""
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = container.view

    results = []
    for host in hosts:
        try:
            vm_values = []
            for vm in host.vm:
                try:
                    mks_value = None
                    for opt in vm.config.extraConfig:
                        if opt.key == "mks.enable3d":
                            mks_value = opt.value
                            break

                    if mks_value is None:
                        # 这里明确标识没有配置，而不是 None
                        mks_value = "Not Configured"

                    vm_values.append({
                        "VM": vm.name,
                        "mks.enable3d": mks_value
                    })

                except Exception as vm_e:
                    logger.error("主机 %s 的 VM %s 获取 mks.enable3d 失败: %s", host.name, vm.name, vm_e)
                    vm_values.append({
                        "VM": vm.name,
                        "mks.enable3d": "Error",
                        "Error": str(vm_e)
                    })

            results.append({
                "AIIB.No": "6.1",
                "Name": "Virtual machines should deactivate 3D graphics features when not required (Automated)",
                "CIS.NO": "7.4",
                "CMD": r'Get-VM -Name $VM | Get-AdvancedSetting mks.enable3d',
                "Host": host.name,
                "Value": vm_values,
                "Description": "Check VM mks.enable3d setting",
                "Error": None
            })
            logger.info("主机: %s, VM 数量: %d", host.name, len(vm_values))

        except Exception as e:
            results.append({
                "AIIB.No": "6.1",
                "Name": "Virtual machines should deactivate 3D graphics features when not required (Automated)",
                "CIS.NO": "7.4",
                "CMD": r'Get-VM -Name $VM | Get-AdvancedSetting mks.enable3d',
                "Host": host.name,
                "Value": [],
                "Description": "Check VM mks.enable3d setting (Error)",
                "Error": str(e)
            })
            logger.error("主机 %s 获取 VM mks.enable3d 配置失败: %s", host.name, e)

    container.Destroy()
    return results


def main(output_dir: str = None):
    if output_dir is None:
        output_dir = "../log"

    output_path = f"{output_dir}/no_6.1_vm_3d_settings.json"

    with VsphereConnection() as si:
        content = si.RetrieveContent()
        vm_3d_info = get_hosts_vm_3d_settings(content)
        export_to_json(vm_3d_info, output_path)

if __name__ == "__main__":
    main()
