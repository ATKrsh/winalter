"""
OOBE & Unattended Setup Provider for WinAlter
Generates autounattend.xml answer files for automated Windows deployment.
"""

import os
from typing import Dict, Any, Optional, Callable
from .base import BaseProvider

class OOBEProvider(BaseProvider):
    def generate_autounattend(self, params: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        username = params.get("username", "Admin")
        password = params.get("password", "")
        computer_name = params.get("computer_name", "WinAlter-PC")
        language = params.get("language", "en-US")
        timezone = params.get("timezone", "UTC")
        skip_oobe = params.get("skip_oobe", True)
        auto_logon = params.get("auto_logon", True)

        if progress_callback:
            progress_callback(f"OOBE Provider: Generating autounattend.xml for user '{username}'...")

        xml_content = fr"""<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
    <settings pass="windowsPE">
        <component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <SetupUILanguage>
                <UILanguage>{language}</UILanguage>
            </SetupUILanguage>
            <InputLocale>{language}</InputLocale>
            <SystemLocale>{language}</SystemLocale>
            <UserLocale>{language}</UserLocale>
            <UILanguage>{language}</UILanguage>
        </component>
        <component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <UserData>
                <AcceptEula>true</AcceptEula>
            </UserData>
            <RunSynchronous>
                <RunSynchronousCommand wcm:action="add">
                    <Order>1</Order>
                    <Path>reg add "HKLM\SYSTEM\Setup\LabConfig" /v BypassTPMCheck /t REG_DWORD /d 1 /f</Path>
                </RunSynchronousCommand>
                <RunSynchronousCommand wcm:action="add">
                    <Order>2</Order>
                    <Path>reg add "HKLM\SYSTEM\Setup\LabConfig" /v BypassRAMCheck /t REG_DWORD /d 1 /f</Path>
                </RunSynchronousCommand>
                <RunSynchronousCommand wcm:action="add">
                    <Order>3</Order>
                    <Path>reg add "HKLM\SYSTEM\Setup\LabConfig" /v BypassSecureBootCheck /t REG_DWORD /d 1 /f</Path>
                </RunSynchronousCommand>
                <RunSynchronousCommand wcm:action="add">
                    <Order>4</Order>
                    <Path>reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE" /v BypassNRO /t REG_DWORD /d 1 /f</Path>
                </RunSynchronousCommand>
            </RunSynchronous>
        </component>
    </settings>
    <settings pass="oobeSystem">
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <ComputerName>{computer_name}</ComputerName>
            <TimeZone>{timezone}</TimeZone>
            <OOBE>
                <HideEULAPage>true</HideEULAPage>
                <HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>
                <HideOnlineAccountScreens>true</HideOnlineAccountScreens>
                <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
                <NetworkLocation>Work</NetworkLocation>
                <ProtectYourPC>3</ProtectYourPC>
                <SkipMachineOOBE>{'true' if skip_oobe else 'false'}</SkipMachineOOBE>
                <SkipUserOOBE>{'true' if skip_oobe else 'false'}</SkipUserOOBE>
            </OOBE>
            <UserAccounts>
                <LocalAccounts>
                    <LocalAccount wcm:action="add">
                        <Name>{username}</Name>
                        <Group>Administrators</Group>
                        <DisplayName>{username}</DisplayName>
                        <Password>
                            <Value>{password}</Value>
                            <PlainText>true</PlainText>
                        </Password>
                    </LocalAccount>
                </LocalAccounts>
            </UserAccounts>
            {'<AutoLogon><Enabled>true</Enabled><Username>' + username + '</Username><Password><Value>' + password + '</Value><PlainText>true</PlainText></Password></AutoLogon>' if auto_logon else ''}
        </component>
    </settings>
</unattend>
"""
        target_xml = params.get("target_path", os.path.join(self.mount_dir, "..", "source", "autounattend.xml"))
        os.makedirs(os.path.dirname(os.path.abspath(target_xml)), exist_ok=True)
        with open(target_xml, "w", encoding="utf-8") as f:
            f.write(xml_content)

        return True
