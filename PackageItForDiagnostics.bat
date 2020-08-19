SET OPTIONS="-y"
	
call PackageIt.bat %OPTIONS%

copy Runit.bat dist\EDScout\

CD dist
"C:\Program Files\7-Zip\7z.exe" a -tzip EDScout-DiagnosticBuild.zip EDScout\

PAUSE