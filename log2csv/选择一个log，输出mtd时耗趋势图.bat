@echo off
cd /d %~dp0
python code\envPrepare.py
python code\Tool.py
python code\log2csv.py
python code\csv2pic_mtdTime.py


echo Finish, terminal will remain 10 mins
timeout /t 600 /nobreak