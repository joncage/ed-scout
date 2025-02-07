; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!
#define Version GetVersionNumbersString('dist-singlefile\EdScout.exe')
#define FullVersion GetStringFileInfo('dist-singlefile\EDScout.exe', 'ProductVersion')

[Setup]
AppId={{2C9BD960-4759-4484-80D2-70047F48AAC4}
AppName=Elite Dangerous Scout
AppVersion={#FullVersion} 
AppPublisher=Jon Cage Software
AppPublisherURL=https://github.com/joncage/ed-scout
AppSupportURL=https://github.com/joncage/ed-scout/issues
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
Source: "eurostile.TTF"; DestDir: "{autofonts}"; FontInstall: "Eurostile"; Flags: onlyifdoesntexist uninsneveruninstall external

[Icons]
Name: "{autoprograms}\EDScout"; Filename: "{app}\EDScout.exe"
Name: "{autodesktop}\EDScout"; Filename: "{app}\EDScout.exe"

[Run]
Filename: {app}\EDScout.exe; Description: Run EDScout now; Flags: postinstall nowait skipifsilent
