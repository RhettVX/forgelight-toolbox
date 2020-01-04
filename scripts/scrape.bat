@echo off
cd %~dp0
..\venv\Scripts\python.exe ..\FLUtils\fl_name_scrape.py scrape %1
pause