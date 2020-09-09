call CreateRelease.bat

DEL /F /Q "dist-installer\*.*"

"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" EdScoutInstaller.iss

FOR /F "tokens=* USEBACKQ" %%F IN (`git describe --tags --dirty`) DO (
SET var=%%F
)
SET RELEASE_DIR=release\%var%\
IF NOT EXIST %RELEASE_DIR% (
MKDIR %RELEASE_DIR%
)


COPY /Y dist-installer\*.exe %RELEASE_DIR%

PAUSE