SET OPTIONS="-y"
SET DIST_NAME="dist-diagnostics"
	
call PackageIt.bat %OPTIONS% %DIST_NAME%

copy Runit.bat %DIST_NAME%\EDScout\

pushd
CD %DIST_NAME%
"C:\Program Files\7-Zip\7z.exe" a -tzip EDScout-DiagnosticBuild.zip EDScout\
cd ..
popd
