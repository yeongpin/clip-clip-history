@echo off
echo Converting PyQt5 imports to PyQt6...

for /r src %%f in (*.py) do (
    echo Processing %%f
    powershell -Command "(Get-Content '%%f') -replace 'PyQt5', 'PyQt6' | Set-Content '%%f'"
    
    REM 修復 QAction 和 QShortcut 位置
    powershell -Command "(Get-Content '%%f') -replace 'from PyQt6.QtWidgets import QAction', '' | Set-Content '%%f'"
    powershell -Command "(Get-Content '%%f') -replace 'from PyQt6.QtWidgets import (.*) QShortcut(.*)', 'from PyQt6.QtWidgets import $1$2' | Set-Content '%%f'"
    powershell -Command "(Get-Content '%%f') -replace 'from PyQt6.QtGui import (.*)', 'from PyQt6.QtGui import $1, QAction, QShortcut' | Set-Content '%%f'"
    
    REM 修復 exec_() 方法
    powershell -Command "(Get-Content '%%f') -replace '\.exec_\(\)', '.exec()' | Set-Content '%%f'"
    
    REM 修復枚舉值
    powershell -Command "(Get-Content '%%f') -replace 'Qt\.UserRole', 'Qt.ItemDataRole.UserRole' | Set-Content '%%f'"
    powershell -Command "(Get-Content '%%f') -replace 'Qt\.CustomContextMenu', 'Qt.ContextMenuPolicy.CustomContextMenu' | Set-Content '%%f'"
    powershell -Command "(Get-Content '%%f') -replace 'QMessageBox\.Yes', 'QMessageBox.StandardButton.Yes' | Set-Content '%%f'"
    powershell -Command "(Get-Content '%%f') -replace 'QMessageBox\.No', 'QMessageBox.StandardButton.No' | Set-Content '%%f'"
    powershell -Command "(Get-Content '%%f') -replace 'QDialog\.Accepted', 'QDialog.DialogCode.Accepted' | Set-Content '%%f'"
    powershell -Command "(Get-Content '%%f') -replace 'QIODevice\.WriteOnly', 'QIODevice.OpenModeFlag.WriteOnly' | Set-Content '%%f'"
)

echo API fixes complete!
pause 