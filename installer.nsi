; ClipClip Installer Script

!include "MUI2.nsh"
!include "FileFunc.nsh"

; Read version from environment variable
!define VERSION $%VERSION%

; General
Name "ClipClip"
OutFile "dist\ClipClip-${VERSION}-setup.exe"
InstallDir "$PROGRAMFILES\ClipClip"
InstallDirRegKey HKCU "Software\ClipClip" ""

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "src\resources\clip_clip_icon.ico"
!define MUI_UNICON "src\resources\clip_clip_icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "ClipClip" SecClipClip
    SetOutPath "$INSTDIR"
    
    ; Add files
    File "dist\ClipClip-${VERSION}-win\ClipClip-${VERSION}-win.exe"
    File "LICENSE"
    File "CHANGELOG.md"
    File "README.md"
    File ".env"
    
    ; Create resources directory
    SetOutPath "$INSTDIR\resources"
    File /r "src\resources\*.*"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\ClipClip"
    CreateShortcut "$SMPROGRAMS\ClipClip\ClipClip.lnk" "$INSTDIR\ClipClip-${VERSION}-win.exe"
    CreateShortcut "$SMPROGRAMS\ClipClip\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Create Desktop shortcut
    CreateShortcut "$DESKTOP\ClipClip.lnk" "$INSTDIR\ClipClip-${VERSION}-win.exe"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Write registry keys
    WriteRegStr HKCU "Software\ClipClip" "" $INSTDIR
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipClip" \
                     "DisplayName" "ClipClip"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipClip" \
                     "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipClip" \
                     "DisplayIcon" "$INSTDIR\resources\clip_clip_icon.ico"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipClip" \
                     "DisplayVersion" "${VERSION}"
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\ClipClip-${VERSION}-win.exe"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\CHANGELOG.md"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\.env"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Remove resources
    RMDir /r "$INSTDIR\resources"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\ClipClip\ClipClip.lnk"
    Delete "$SMPROGRAMS\ClipClip\Uninstall.lnk"
    Delete "$DESKTOP\ClipClip.lnk"
    RMDir "$SMPROGRAMS\ClipClip"
    
    ; Remove registry keys
    DeleteRegKey HKCU "Software\ClipClip"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipClip"
    
    ; Remove installation directory
    RMDir /r "$INSTDIR"
SectionEnd 