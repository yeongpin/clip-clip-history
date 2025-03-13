# -*- mode: python ; coding: utf-8 -*-
import os
import platform
from dotenv import load_dotenv

load_dotenv()

# load version from .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('version'):
            version = line.split('=')[1].strip()
            break
    else:
        version = '1.0.0'

# set output name based on system type
system = platform.system().lower()
if system == "windows":
    os_type = "win"
    icon_file = 'src/resources/clip_clip_icon.ico'
elif system == "linux":
    os_type = "linux"
    icon_file = 'src/resources/clip_clip_icon.svg'
else:  # Darwin
    os_type = "mac"
    icon_file = 'src/resources/clip_clip_icon.icns'

output_name = f"ClipClip-{version}-{os_type}"

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env', '.'),
        ('CHANGELOG.md', '.'),
        ('LICENSE', '.'),
        ('README.md', '.'),
        ('src/resources', 'resources')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

target_arch = os.environ.get('TARGET_ARCH', None)

if system == "darwin":  # macOS
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=output_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=target_arch,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=True,
        upx=True,
        upx_exclude=['Qt6'],
        name=output_name
    )
    
    app = BUNDLE(
        coll,
        name=f"{output_name}.app",
        icon=icon_file,
        bundle_identifier="com.clipclip.app",
        info_plist={
            'LSUIElement': False,  # 改為 False，讓應用在 Dock 中顯示
            'NSHighResolutionCapable': True,
            'CFBundleDisplayName': 'ClipClip',
            'CFBundleName': 'ClipClip',
            'CFBundleExecutable': output_name
        }
    )

elif system == "linux":  # Linux
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=output_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=True,
        upx=True,
        upx_exclude=['Qt6'],
        name=output_name
    )
    
    # Create .desktop file
    with open(f"dist/{output_name}.desktop", "w") as f:
        f.write(f"""[Desktop Entry]
Name=ClipClip
Exec=/usr/local/bin/clipclip
Icon=clipclip
Type=Application
Categories=Utility;
""")

else:  # Windows
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=output_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file
    )
