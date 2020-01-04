@echo off
cd %~dp0
..\venv\Scripts\python.exe ..\FLUtils\fl_index.py diff %1 %2
pause