; -- Example2.iss --
; Same as Example1.iss, but creates its icon in the Programs folder of the
; Start Menu instead of in a subfolder, and also creates a desktop icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!
#define Version GetFileVersion('dist-singlefile\EdScout.exe')

[Setup]
AppId={{2C9BD960-4759-4484-80D2-70047F48AAC4}
AppName=Elite Dangerous Scout
AppVersion=LoadStringFromFile('version.txt', ANSIStr)
WizardStyle=modern
DefaultDirName={autopf}\EDScout
; Since no icons will be created in "{group}", we don't need the wizard
; to ask for a Start Menu folder name:
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\EDScout.exe

Compression=lzma2
SolidCompression=yes
OutputDir="dist-installer"
OutputBaseFilename="Setup-EdScout-{#Version}"
SetupIconFile=..\EDScoutWebUI\static\favicon.ico

[Files]
Source: "dist-singlefile\EDScout.exe"; DestDir: "{app}"
; Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{autoprograms}\EDScout"; Filename: "{app}\EDScout.exe"
Name: "{autodesktop}\EDScout"; Filename: "{app}\EDScout.exe"

[Run]
Filename: {app}\EDScout.exe; Description: Run EDScout now; Flags: postinstall nowait skipifsilent
