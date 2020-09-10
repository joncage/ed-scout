call PackageIt.bat

IF %ERRORLEVEL% NEQ 0 GOTO END

cd dist\
EDScout.exe

:END
PAUSE
exit %ERRORLEVEL%
