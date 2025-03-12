@echo off
echo Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo Done!
pause 