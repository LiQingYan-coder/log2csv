@echo off
cd /d %~dp0
python src\envPrepare.py
python src\Tool.py
python src\log2csv.py
python src\csv2pic_mtdTime.py


echo Finish, terminal will remain 10 mins
timeout /t 600 /nobreak