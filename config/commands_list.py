commands = [
    {"NO": "1.1", "name": "Host must run software that has not reached End of General Support status", "CIS.NO": "2.1",
     "cmd": 'None'},
    {"NO": "1.2", "name": "Host must have reliable time synchronization sources", "CIS.NO": "2.6",
     "cmd": r'Get-VMHost | Select-Object Name, @{Name="NTPSetting"; Expression={ ($_ | Get-VMHostNtpServer)}}'},
    {"NO": "1.3", "name": "Host must have time synchronization services enabled and running (Manual)", "CIS.NO": "2.7",
     "cmd": 'None'},
    {"NO": "1.4", "name": "Host must restrict inter-VM transparent page sharing (Automated)", "CIS.NO": "2.10",
     "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description'},
    {"NO": "2.1", "name": "Host should deactivate SSH (Automated)", "CIS.NO": "3.1",
     "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select Key, Label, Policy, Running, Required'},
    {"NO": "2.2", "name": "Host must deactivate the ESXi shell (Automated)", "CIS.NO": "3.2",
     "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM" } | Select Key, Label, Policy, Running, Required'},
    {"NO": "2.3", "name": "Host must deactivate the ESXi Managed Object Browser (MOB) (Automated)", "CIS.NO": "3.4",
     "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Config.HostAgent.plugins.solo.enableMob | Select Name, Value, Type, Description'},
    {
        "NO": "2.4",
        "name": "Host should deactivate SNMP (Manual)",
        "CIS.NO": "3.6",
        "cmd": 'None'
    },
    {
        "NO": "2.5",
        "name": "Host must automatically terminate idle DCUI sessions (Automated)",
        "CIS.NO": "3.7",
        "cmd": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.DcuiTimeOut'
    },
    {
        "NO": "2.6",
        "name": "Host must not suppress warnings that the shell is enabled (Manual)",
        "CIS.NO": "3.10",
        "cmd": 'None'
    },
    {
        "NO": "2.7",
        "name": "Host must enforce password complexity (Manual)",
        "CIS.NO": "3.11",
        "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select VMHost, Key, Label, Policy, Running, Required'
    },
    {
        "NO": "2.8",
        "name": "Host must lock an account after a specified number of failed login attempts (Automated)",
        "CIS.NO": "3.12",
        "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountLockFailure'
    },
    {
        "NO": "2.9",
        "name": "Host must unlock accounts after a specified timeout period (Automated)",
        "CIS.NO": "3.13",
        "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime'
    },
    {
        "NO": "2.10",
        "name": "Host must configure the password history setting to restrict the reuse of passwords (Manual)",
        "CIS.NO": "3.14",
        "cmd": r'Get-VMHost | Get-AdvancedSetting Security.PasswordHistory'
    },
    {
        "NO": "2.11",
        "name": "Host must be configured with an appropriate maximum password age (Manual)",
        "CIS.NO": "3.15",
        "cmd": 'None'
    },
    {
        "NO": "2.12",
        "name": "Host must configure a session timeout for the API (Manual)",
        "CIS.NO": "3.16",
        "cmd": 'None'
    },
    {
        "NO": "2.13",
        "name": "Host must automatically terminate idle host client sessions (Manual)",
        "CIS.NO": "3.17",
        "cmd": 'None'
    },
    {
        "NO": "2.14",
        "name": "Host must have an accurate DCUI.Access list (Manual)",
        "CIS.NO": "3.18",
        "cmd": r'Get-VMHost | Get-AdvancedSetting -Name DCUI.Access'
    },
    {
        "NO": "2.15",
        "name": "Host must have an accurate Exception Users list (Manual)",
        "CIS.NO": "3.19",
        "cmd": 'None'
    },
    {
        "NO": "2.16",
        "name": "Host must enable the highest version of TLS supported (Manual)",
        "CIS.NO": "3.26",
        "cmd": 'None'
    },
    {
        "NO": "3.1",
        "name": "Host must configure a persistent log location for all locally stored system logs (Manual)",
        "CIS.NO": "4.1",
        "cmd": r'Get-VMHost | Select Name, @{N="Syslog.global.logDir";E={$_ | Get-AdvancedConfiguration Syslog.global.logDir | Select -ExpandProperty Values}}'
    },
    {
        "NO": "3.2",
        "name": "Host must transmit system logs to a remote log collector (Automated)",
        "CIS.NO": "4.2",
        "cmd": r'Get-VMHost | Select Name, @{N="Syslog.global.logHost";E={$_ | Get-AdvancedSetting Syslog.global.logHost}}'
    },
    {
        "NO": "3.3",
        "name": "Host must set the logging informational level to info (Manual)",
        "CIS.NO": "4.4",
        "cmd": 'None'
    },
    {
        "NO": "3.4",
        "name": "Host must deactivate log filtering (Manual)",
        "CIS.NO": "4.5",
        "cmd": 'None'
    },
    {
        "NO": "3.5",
        "name": "Host must verify certificates for TLS remote logging endpoints (Manual)",
        "CIS.NO": "4.10",
        "cmd": 'None'
    },
    {
        "NO": "4.1",
        "name": "Host firewall must only allow traffic from authorized networks (Manual)",
        "CIS.NO": "5.1",
        "cmd": r'Get-VMHost HOST1 | Get-VMHostService'
    },
    {
        "NO": "4.2",
        "name": "Host must restrict use of the dvFilter network API (Manual)",
        "CIS.NO": "5.3",
        "cmd": r'Get-VMHost | Select Name, @{N="Net.DVFilterBindIpAddress";E={$_ | Get-AdvancedSetting Net.DVFilterBindIpAddress | Select -ExpandProperty Values}}'
    },
    {
        "NO": "4.3",
        "name": "Host must filter Bridge Protocol Data Unit (BPDU) packets (Manual)",
        "CIS.NO": "5.4",
        "cmd": 'None'
    },
    {
        "NO": "4.4",
        "name": "Host should reject forged transmits on standard virtual switches and port groups (Automated)",
        "CIS.NO": "5.6",
        "cmd": r'Get-VirtualSwitch -Standard | Select VMHost, Name, `@{N="MacChanges";E={if ($_.ExtensionData.Spec.Policy.Security.MacChanges) {"Accept"} Else {"Reject"} }}, `@{N="PromiscuousMode";E={if ($_.ExtensionData.Spec.Policy.Security.PromiscuousMode) {"Accept"} Else {"Reject"} }}, `@{N="ForgedTransmits";E={if ($_.ExtensionData.Spec.Policy.Security.ForgedTransmits) {"Accept"} Else {"Reject"} }}'
    },
    {
        "NO": "4.5",
        "name": "Host should reject MAC address changes on standard virtual switches and port groups (Automated)",
        "CIS.NO": "5.7",
        "cmd": r'Get-VirtualSwitch -Standard | Select VMHost, Name, `@{N="MacChanges";E={if ($_.ExtensionData.Spec.Policy.Security.MacChanges) {"Accept"} Else {"Reject"} }}, `@{N="PromiscuousMode";E={if ($_.ExtensionData.Spec.Policy.Security.PromiscuousMode) {"Accept"} Else {"Reject"} }}, `@{N="ForgedTransmits";E={if ($_.ExtensionData.Spec.Policy.Security.ForgedTransmits) {"Accept"} Else {"Reject"} }}'
    },
    {
        "NO": "4.6",
        "name": "Host should reject promiscuous mode requests on standard virtual switches and port groups (Automated)",
        "CIS.NO": "5.8",
        "cmd": r'Get-VirtualSwitch -Standard | Select VMHost, Name, `@{N="MacChanges";E={if ($_.ExtensionData.Spec.Policy.Security.MacChanges) {"Accept"} Else {"Reject"} }}, `@{N="PromiscuousMode";E={if ($_.ExtensionData.Spec.Policy.Security.PromiscuousMode) {"Accept"} Else {"Reject"} }}, `@{N="ForgedTransmits";E={if ($_.ExtensionData.Spec.Policy.Security.ForgedTransmits) {"Accept"} Else {"Reject"} }}'
    },
    {
        "NO": "4.7",
        "name": "Host must restrict access to a default or native VLAN on standard virtual switches (Automated)",
        "CIS.NO": "5.9",
        "cmd": r'Get-VirtualPortGroup -Standard | Select virtualSwitch, Name, VlanID'
    },
    {
        "NO": "4.8",
        "name": "Host must restrict the use of Virtual Guest Tagging (VGT) on standard virtual switches (Automated)",
        "CIS.NO": "5.10",
        "cmd": r'Get-VirtualPortGroup -Standard | Select virtualSwitch, Name, VlanID'
    },
    {
        "NO": "4.9",
        "name": "Host must isolate management communications (Manual)",
        "CIS.NO": "5.11",
        "cmd": 'None'
    },
    {
        "NO": "5.1",
        "name": "Host must ensure all datastores have unique names (Manual)",
        "CIS.NO": "6.2.2",
        "cmd": 'None'
    },
    {
        "NO": "6.1",
        "name": "Virtual machines should deactivate 3D graphics features when not required (Automated)",
        "CIS.NO": "7.4",
        "cmd": r'Get-VM -Name $VM | Get-AdvancedSetting mks.enable3d'
    },
    {
        "NO": "6.2",
        "name": "Virtual machines must limit PCI/PCIe device passthrough functionality (Automated)",
        "CIS.NO": "7.7",
        "cmd": r'Get-VM | Get-AdvancedSetting -Name "pciPassthru*.present" | Select Entity, Name, Value'
    },
    {
        "NO": "6.3",
        "name": "Virtual machines must remove unnecessary audio devices (Manual)",
        "CIS.NO": "7.10",
        "cmd": 'None'
    },
    {
        "NO": "6.4",
        "name": "Virtual machines must remove unnecessary AHCI devices (Manual)",
        "CIS.NO": "7.11",
        "cmd": 'None'
    },
    {
        "NO": "6.5",
        "name": "Virtual machines must remove unnecessary USB/XHCI devices (Automated)",
        "CIS.NO": "7.12",
        "cmd": r'Get-VM | Get-USBDevice'
    },
    {
        "NO": "6.6",
        "name": "Virtual machines must remove unnecessary serial port devices (Automated)",
        "CIS.NO": "7.13",
        "cmd": r'Get-VM | Get-SerialPort'
    },
    {
        "NO": "6.7",
        "name": "Virtual machines must remove unnecessary parallel port devices (Automated)",
        "CIS.NO": "7.14",
        "cmd": r'Get-VM | Get-ParallelPort'
    },
    {
        "NO": "6.8",
        "name": "Virtual machines must remove unnecessary CD/DVD devices (Automated)",
        "CIS.NO": "7.15",
        "cmd": r'Get-VM | Get-CDDrive'
    },
    {
        "NO": "6.9",
        "name": "Virtual machines must remove unnecessary floppy devices (Automated)",
        "CIS.NO": "7.16",
        "cmd": r'Get-VM | Get-FloppyDrive | Select Parent, Name, ConnectionState'
    },
    {
        "NO": "7.0",
        "name": "Virtual machines should have virtual machine hardware version 19 or newer (Manual)",
        "CIS.NO": "7.29",
        "cmd": 'None'
    },
    {
        "NO": "7.1",
        "name": "VMware Tools must have all software updates installed (Manual)",
        "CIS.NO": "8.2",
        "cmd": 'None'
    },
    {
        "NO": "7.2",
        "name": "VMware Tools should configure automatic upgrades as appropriate for the environment (Manual)",
        "CIS.NO": "8.3",
        "cmd": 'None'
    },
    {
        "NO": "7.3",
        "name": "VMware Tools on deployed virtual machines must prevent being recustomized (Manual)",
        "CIS.NO": "8.4",
        "cmd": 'None'
    }
]

commands_test = [
    {"NO":"1.1", "name": "Host must run software that has not reached End of General Support status", "CIS.NO":"2.1", "cmd": 'None'},
    {"NO":"1.2", "name": "Host must have reliable time synchronization sources", "CIS.NO":"2.6", "cmd": r'Get-VMHost | Select-Object Name, @{Name="NTPSetting"; Expression={ ($_ | Get-VMHostNtpServer)}}'},
    {"NO":"1.3", "name": "Host must have time synchronization services enabled and running (Manual)", "CIS.NO":"2.7", "cmd": 'None'},
    {"NO":"1.4", "name": "Host must restrict inter-VM transparent page sharing (Automated)", "CIS.NO":"2.10", "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description'},
    {"NO": "2.1", "name": "Host should deactivate SSH (Automated)", "CIS.NO": "3.1", "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select Key, Label, Policy, Running, Required'},
    {"NO": "2.2", "name": "Host must deactivate the ESXi shell (Automated)", "CIS.NO": "3.2", "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM" } | Select Key, Label, Policy, Running, Required'},
    {"NO": "2.3", "name": "Host must deactivate the ESXi Managed Object Browser (MOB) (Automated)", "CIS.NO": "3.4", "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Config.HostAgent.plugins.solo.enableMob | Select Name, Value, Type, Description'},
    {"NO": "2.4","name": "Host should deactivate SNMP (Manual)","CIS.NO": "3.6","cmd": 'None'},
    {"NO": "2.5","name": "Host must automatically terminate idle DCUI sessions (Automated)","CIS.NO": "3.7","cmd": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.DcuiTimeOut'},
]

commands_def = [
    {"NO": "1.1", "name": "Host must run software that has not reached End of General Support status", "CIS.NO": "2.1",
     "cmd": 'None'},
    {"NO": "1.2", "name": "Host must have reliable time synchronization sources", "CIS.NO": "2.6",
     "cmd": r'Get-VMHost | Select-Object Name, @{Name="NTPSetting"; Expression={ ($_ | Get-VMHostNtpServer)}}'},
    {"NO": "1.3", "name": "Host must have time synchronization services enabled and running (Manual)", "CIS.NO": "2.7",
     "cmd": 'None'},
    {"NO": "1.4", "name": "Host must restrict inter-VM transparent page sharing (Automated)", "CIS.NO": "2.10",
     "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Mem.ShareForceSalting | Select-Object Name, Value, Type, Description'},
    {"NO": "2.1", "name": "Host should deactivate SSH (Automated)", "CIS.NO": "3.1",
     "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select Key, Label, Policy, Running, Required'},
    {"NO": "2.2", "name": "Host must deactivate the ESXi shell (Automated)", "CIS.NO": "3.2",
     "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM" } | Select Key, Label, Policy, Running, Required'},
    {"NO": "2.3", "name": "Host must deactivate the ESXi Managed Object Browser (MOB) (Automated)", "CIS.NO": "3.4",
     "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Config.HostAgent.plugins.solo.enableMob | Select Name, Value, Type, Description'},
    {
        "NO": "2.4",
        "name": "Host should deactivate SNMP (Manual)",
        "CIS.NO": "3.6",
        "cmd": 'None'
    },
    {
        "NO": "2.5",
        "name": "Host must automatically terminate idle DCUI sessions (Automated)",
        "CIS.NO": "3.7",
        "cmd": r'Get-VMHost | Get-AdvancedSetting -Name UserVars.DcuiTimeOut'
    },
    {
        "NO": "2.6",
        "name": "Host must not suppress warnings that the shell is enabled (Manual)",
        "CIS.NO": "3.10",
        "cmd": 'None'
    },
    {
        "NO": "2.7",
        "name": "Host must enforce password complexity (Manual)",
        "CIS.NO": "3.11",
        "cmd": r'Get-VMHost | Get-VMHostService | Where { $_.key -eq "TSM-SSH" } | Select VMHost, Key, Label, Policy, Running, Required'
    },
    {
        "NO": "2.8",
        "name": "Host must lock an account after a specified number of failed login attempts (Automated)",
        "CIS.NO": "3.12",
        "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountLockFailure'
    },
    {
        "NO": "2.9",
        "name": "Host must unlock accounts after a specified timeout period (Automated)",
        "CIS.NO": "3.13",
        "cmd": r'Get-VMHost | Get-AdvancedSetting -Name Security.AccountUnlockTime'
    },
    {
        "NO": "2.10",
        "name": "Host must configure the password history setting to restrict the reuse of passwords (Manual)",
        "CIS.NO": "3.14",
        "cmd": r'Get-VMHost | Get-AdvancedSetting Security.PasswordHistory'
    },
    {
        "NO": "2.11",
        "name": "Host must be configured with an appropriate maximum password age (Manual)",
        "CIS.NO": "3.15",
        "cmd": 'None'
    },
    {
        "NO": "2.12",
        "name": "Host must configure a session timeout for the API (Manual)",
        "CIS.NO": "3.16",
        "cmd": 'None'
    },
    {
        "NO": "2.13",
        "name": "Host must automatically terminate idle host client sessions (Manual)",
        "CIS.NO": "3.17",
        "cmd": 'None'
    },
    {
        "NO": "2.14",
        "name": "Host must have an accurate DCUI.Access list (Manual)",
        "CIS.NO": "3.18",
        "cmd": r'Get-VMHost | Get-AdvancedSetting -Name DCUI.Access'
    },
    {
        "NO": "2.15",
        "name": "Host must have an accurate Exception Users list (Manual)",
        "CIS.NO": "3.19",
        "cmd": 'None'
    },
    {
        "NO": "2.16",
        "name": "Host must enable the highest version of TLS supported (Manual)",
        "CIS.NO": "3.26",
        "cmd": 'None'
    },
    {
        "NO": "3.1",
        "name": "Host must configure a persistent log location for all locally stored system logs (Manual)",
        "CIS.NO": "4.1",
        "cmd": r'Get-VMHost | Select Name, @{N="Syslog.global.logDir";E={$_ | Get-AdvancedConfiguration Syslog.global.logDir | Select -ExpandProperty Values}}'
    },
    {
        "NO": "3.2",
        "name": "Host must transmit system logs to a remote log collector (Automated)",
        "CIS.NO": "4.2",
        "cmd": r'Get-VMHost | Select Name, @{N="Syslog.global.logHost";E={$_ | Get-AdvancedSetting Syslog.global.logHost}}'
    },
    {
        "NO": "3.3",
        "name": "Host must set the logging informational level to info (Manual)",
        "CIS.NO": "4.4",
        "cmd": 'None'
    },
    {
        "NO": "3.4",
        "name": "Host must deactivate log filtering (Manual)",
        "CIS.NO": "4.5",
        "cmd": 'None'
    },
    {
        "NO": "3.5",
        "name": "Host must verify certificates for TLS remote logging endpoints (Manual)",
        "CIS.NO": "4.10",
        "cmd": 'None'
    },
    {
        "NO": "4.1",
        "name": "Host firewall must only allow traffic from authorized networks (Manual)",
        "CIS.NO": "5.1",
        "cmd": r'Get-VMHost HOST1 | Get-VMHostService'
    },
    {
        "NO": "4.2",
        "name": "Host must restrict use of the dvFilter network API (Manual)",
        "CIS.NO": "5.3",
        "cmd": r'Get-VMHost | Select Name, @{N="Net.DVFilterBindIpAddress";E={$_ | Get-AdvancedSetting Net.DVFilterBindIpAddress | Select -ExpandProperty Values}}'
    },
    {
        "NO": "4.3",
        "name": "Host must filter Bridge Protocol Data Unit (BPDU) packets (Manual)",
        "CIS.NO": "5.4",
        "cmd": 'None'
    },
    {
        "NO": "4.4",
        "name": "Host should reject forged transmits on standard virtual switches and port groups (Automated)",
        "CIS.NO": "5.6",
        "cmd": r'Get-VirtualSwitch -Standard | Select VMHost, Name, `@{N="MacChanges";E={if ($_.ExtensionData.Spec.Policy.Security.MacChanges) {"Accept"} Else {"Reject"} }}, `@{N="PromiscuousMode";E={if ($_.ExtensionData.Spec.Policy.Security.PromiscuousMode) {"Accept"} Else {"Reject"} }}, `@{N="ForgedTransmits";E={if ($_.ExtensionData.Spec.Policy.Security.ForgedTransmits) {"Accept"} Else {"Reject"} }}'
    },
    {
        "NO": "4.5",
        "name": "Host should reject MAC address changes on standard virtual switches and port groups (Automated)",
        "CIS.NO": "5.7",
        "cmd": r'Get-VirtualSwitch -Standard | Select VMHost, Name, `@{N="MacChanges";E={if ($_.ExtensionData.Spec.Policy.Security.MacChanges) {"Accept"} Else {"Reject"} }}, `@{N="PromiscuousMode";E={if ($_.ExtensionData.Spec.Policy.Security.PromiscuousMode) {"Accept"} Else {"Reject"} }}, `@{N="ForgedTransmits";E={if ($_.ExtensionData.Spec.Policy.Security.ForgedTransmits) {"Accept"} Else {"Reject"} }}'
    },
    {
        "NO": "4.6",
        "name": "Host should reject promiscuous mode requests on standard virtual switches and port groups (Automated)",
        "CIS.NO": "5.8",
        "cmd": r'Get-VirtualSwitch -Standard | Select VMHost, Name, `@{N="MacChanges";E={if ($_.ExtensionData.Spec.Policy.Security.MacChanges) {"Accept"} Else {"Reject"} }}, `@{N="PromiscuousMode";E={if ($_.ExtensionData.Spec.Policy.Security.PromiscuousMode) {"Accept"} Else {"Reject"} }}, `@{N="ForgedTransmits";E={if ($_.ExtensionData.Spec.Policy.Security.ForgedTransmits) {"Accept"} Else {"Reject"} }}'
    },
    {
        "NO": "4.7",
        "name": "Host must restrict access to a default or native VLAN on standard virtual switches (Automated)",
        "CIS.NO": "5.9",
        "cmd": r'Get-VirtualPortGroup -Standard | Select virtualSwitch, Name, VlanID'
    },
    {
        "NO": "4.8",
        "name": "Host must restrict the use of Virtual Guest Tagging (VGT) on standard virtual switches (Automated)",
        "CIS.NO": "5.10",
        "cmd": r'Get-VirtualPortGroup -Standard | Select virtualSwitch, Name, VlanID'
    },
    {
        "NO": "4.9",
        "name": "Host must isolate management communications (Manual)",
        "CIS.NO": "5.11",
        "cmd": 'None'
    },{
        "NO": "5.1",
        "name": "Host must ensure all datastores have unique names (Manual)",
        "CIS.NO": "6.2.2",
        "cmd": 'None'
    },
    {
        "NO": "6.1",
        "name": "Virtual machines should deactivate 3D graphics features when not required (Automated)",
        "CIS.NO": "7.4",
        "cmd": r'Get-VM -Name $VM | Get-AdvancedSetting mks.enable3d'
    },
    {
        "NO": "6.2",
        "name": "Virtual machines must limit PCI/PCIe device passthrough functionality (Automated)",
        "CIS.NO": "7.7",
        "cmd": r'Get-VM | Get-AdvancedSetting -Name "pciPassthru*.present" | Select Entity, Name, Value'
    },
    {
        "NO": "6.3",
        "name": "Virtual machines must remove unnecessary audio devices (Manual)",
        "CIS.NO": "7.10",
        "cmd": 'None'
    },
    {
        "NO": "6.4",
        "name": "Virtual machines must remove unnecessary AHCI devices (Manual)",
        "CIS.NO": "7.11",
        "cmd": 'None'
    },
    {
        "NO": "6.5",
        "name": "Virtual machines must remove unnecessary USB/XHCI devices (Automated)",
        "CIS.NO": "7.12",
        "cmd": r'Get-VM | Get-USBDevice'
    },
    {
        "NO": "6.6",
        "name": "Virtual machines must remove unnecessary serial port devices (Automated)",
        "CIS.NO": "7.13",
        "cmd": r'Get-VM | Get-SerialPort'
    },
    {
        "NO": "6.7",
        "name": "Virtual machines must remove unnecessary parallel port devices (Automated)",
        "CIS.NO": "7.14",
        "cmd": r'Get-VM | Get-ParallelPort'
    },
    {
        "NO": "6.8",
        "name": "Virtual machines must remove unnecessary CD/DVD devices (Automated)",
        "CIS.NO": "7.15",
        "cmd": r'Get-VM | Get-CDDrive'
    },
    {
        "NO": "6.9",
        "name": "Virtual machines must remove unnecessary floppy devices (Automated)",
        "CIS.NO": "7.16",
        "cmd": r'Get-VM | Get-FloppyDrive | Select Parent, Name, ConnectionState'
    },
    {
        "NO": "7.0",
        "name": "Virtual machines should have virtual machine hardware version 19 or newer (Manual)",
        "CIS.NO": "7.29",
        "cmd": 'None'
    },
    {
        "NO": "7.1",
        "name": "VMware Tools must have all software updates installed (Manual)",
        "CIS.NO": "8.2",
        "cmd": 'None'
    },
    {
        "NO": "7.2",
        "name": "VMware Tools should configure automatic upgrades as appropriate for the environment (Manual)",
        "CIS.NO": "8.3",
        "cmd": 'None'
    },
    {
        "NO": "7.3",
        "name": "VMware Tools on deployed virtual machines must prevent being recustomized (Manual)",
        "CIS.NO": "8.4",
        "cmd": 'None'
    }
]

def commands_list_def():
    """ 根据环境 env 获取 vsphere 配置信息 """
    return commands_def

def commands_list_test():
    return commands_test
if __name__ == "__main__":
    print(commands_list_test())

