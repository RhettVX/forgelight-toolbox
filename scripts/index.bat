@echo off
cd %~dp0
..\venv\Scripts\python.exe ..\FLUtils\fl_index.py index -n merged-names.txt %*
pause