FOR /F "tokens=* USEBACKQ" %%F IN (`git describe --tags --dirty`) DO (
SET var=%%F
)
SET RELEASE_DIR=release\%var%\
IF NOT EXIST %RELEASE_DIR% (
MKDIR %RELEASE_DIR%
)

CALL PackageItForSingleFile.bat
COPY /Y dist-singlefile\EDScout.exe %RELEASE_DIR%

CALL PackageItForDiagnostics.bat
COPY /Y dist-diagnostics\EDScout-DiagnosticBuild.zip %RELEASE_DIR%
