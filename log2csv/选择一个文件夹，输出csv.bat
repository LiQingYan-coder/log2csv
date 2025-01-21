@echo off
cd /d %~dp0
python src\envPrepare.py
python src\Tool.py
python src\folder2pics.py


echo ######### Finish, terminal will remain 10 mins #########
timeout /t 600 /nobreak