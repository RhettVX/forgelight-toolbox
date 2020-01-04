@echo off
cd %~dp0
..\venv\Scripts\python.exe ..\FLUtils\fl_pack.py unpack -n merged-names.txt %*
pause