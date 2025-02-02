; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!
#define Version GetVersionNumbersString('dist-singlefile\EdScout.exe')
#define FullVersion GetStringFileInfo('dist-singlefile\EDScout.exe', 'ProductVersion')

[Setup]
AppId={{2C9BD960-4759-4484-80D2-70047F48AAC4}
AppName=Elite Dangerous Scout
AppVersion={#FullVersion} 
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
Source: "{tmp}\eurostile.TTF"; DestDir: "{autofonts}"; FontInstall: "Eurostile"; Flags: onlyifdoesntexist uninsneveruninstall external

[Icons]
Name: "{autoprograms}\EDScout"; Filename: "{app}\EDScout.exe"
Name: "{autodesktop}\EDScout"; Filename: "{app}\EDScout.exe"

[Run]
Filename: {app}\EDScout.exe; Description: Run EDScout now; Flags: postinstall nowait skipifsilent

[Code]
const
  SHCONTCH_NOPROGRESSBOX = 4;
  SHCONTCH_RESPONDYESTOALL = 16;

procedure dw(ZipPath, TargetPath: string); 
var
  Shell: Variant;
  ZipFile: Variant;
  TargetFolder: Variant;
begin
  Shell := CreateOleObject('Shell.Application');

  ZipFile := Shell.NameSpace(ZipPath);
  if VarIsClear(ZipFile) then
    RaiseException(Format('ZIP file "%s" does not exist or cannot be opened', [ZipPath]));

  TargetFolder := Shell.NameSpace(TargetPath);
  if VarIsClear(TargetFolder) then
    RaiseException(Format('Target path "%s" does not exist', [TargetPath]));

  TargetFolder.CopyHere(ZipFile.Items, SHCONTCH_NOPROGRESSBOX or SHCONTCH_RESPONDYESTOALL);
end;

function OnDownloadProgress(const Url, Filename: string; const Progress, ProgressMax: Int64): Boolean;
begin
  if ProgressMax <> 0 then
    Log(Format('  %d of %d bytes done.', [Progress, ProgressMax]))
  else
    Log(Format('  %d bytes done.', [Progress]));
  Result := True;
end;

function InitializeSetup: Boolean;
begin
  try
    DownloadTemporaryFile('https://www.cufonfonts.com/download/rf/eurostile', 'eurostile-cufonfonts.zip', '', @OnDownloadProgress);
    dw(ExpandConstant('{tmp}')+'\eurostile-cufonfonts.zip', ExpandConstant('{tmp}'));
    Result := True;
  except
    Log(GetExceptionMessage);
    Result := False;
  end;
end;