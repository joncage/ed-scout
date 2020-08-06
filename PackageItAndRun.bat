REM pipenv run pyinstaller EDScout-WebUI\WebUI.py
pipenv run pyinstaller ^
    --hidden-import=eventlet.hubs.epolls ^
    --hidden-import=eventlet.hubs.kqueue ^
    --hidden-import=eventlet.hubs.selects ^
    --hidden-import=zmq ^
    --hidden-import=dns ^
    --hidden-import=dns.dnssec ^
    --hidden-import=dns.e164 ^
    --hidden-import=dns.hash ^
    --hidden-import=dns.namedict ^
    --hidden-import=dns.tsigkeyring ^
    --hidden-import=dns.update ^
    --hidden-import=dns.version ^
    --hidden-import=dns.zone ^
    --hidden-import=engineio.async_drivers ^
    --hidden-import=engineio.async_drivers.eventlet ^
    --hidden-import=engineio.server ^
    --hidden-import=flaskwebgui ^
    --onedir EDScout-WebUI\WebUI.py 


IF %ERRORLEVEL% NEQ 0 GOTO END

dist\WebUI\WebUI.exe

:END
PAUSE
exit %ERRORLEVEL%
