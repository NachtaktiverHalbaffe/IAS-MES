@echo off
set IP_ADRESS="192.168.178.30"

ECHO Starting backend...
cd C:\Users\NachtaktiverHalbaffe\Documents\Git\IAS_MES\
CALL venv\Scripts\activate
cd .\backend\
start cmd /k waitress-serve --listen=%IP_ADRESS%:8000 --threads=10 backend.wsgi:application


ECHO Backend started. Now starting Frontend...
cd ..\frontend\
CALL deactivate
start cmd /k serve -l tcp://%IP_ADRESS%:8080 build
ECHO Sucessfully started MES
start "" http://%IP_ADRESS%:8080/