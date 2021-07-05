@echo off
ECHO Starting backend...
cd C:\Users\NachtaktiverHalbaffe\Documents\Git\IAS_MES\
CALL venv\Scripts\activate
cd .\backend\
start cmd /k waitress-serve --listen=192.168.178.30:8000 --threads=6 backend.wsgi:application


ECHO Backend started. Now starting Frontend...
cd ..\frontend\
CALL deactivate
start cmd /k serve -l tcp://192.168.178.30:8080 build
ECHO Sucessfully started MES