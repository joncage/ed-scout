SET OPTIONS="-y"
	
call PackageIt.bat %OPTIONS%

copy Runit.bat dist\EDScout\

pushd
CD dist
"C:\Program Files\7-Zip\7z.exe" a -tzip EDScout-DiagnosticBuild.zip EDScout\
cd ..
popd
