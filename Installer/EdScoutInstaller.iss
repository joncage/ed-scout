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
var
  DownloadPage: TDownloadWizardPage;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded file to {tmp}: %s', [FileName]));
  Result := True;
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
  DownloadPage.ShowBaseNameInsteadOfUrl := True;
end;

const
  NO_PROGRESS_BOX = 4;
  RESPOND_YES_TO_ALL = 16;

procedure UnZip(ZipPath, FileName, TargetPath: string); 
var
  Shell: Variant;
  ZipFile: Variant;
  Item: Variant;
  TargetFolder: Variant;
begin
  Shell := CreateOleObject('Shell.Application');

  ZipFile := Shell.NameSpace(ZipPath);
  if VarIsClear(ZipFile) then
    RaiseException(Format('Cannot open ZIP file "%s" or does not exist', [ZipPath]));

  Item := ZipFile.ParseName(FileName);
  if VarIsClear(Item) then
    RaiseException(Format('Cannot find "%s" in "%s" ZIP file', [FileName, ZipPath]));

  TargetFolder := Shell.NameSpace(TargetPath);
  if VarIsClear(TargetFolder) then
    RaiseException(Format('Target path "%s" does not exist', [TargetPath]));

  TargetFolder.CopyHere(Item, NO_PROGRESS_BOX or RESPOND_YES_TO_ALL);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    // Use AddEx to specify a username and password
    DownloadPage.Add('https://font.download/dl/font/eurostile-2.zip', 'eurostile-font.zip', '');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download; // This downloads the files to {tmp}
        UnZip(ExpandConstant('{tmp}\eurostile-font.zip'), 'eurostile.TTF', ExpandConstant('{tmp}'));
        Result := True;
      except
        if DownloadPage.AbortedByUser then
          Log('Aborted by user.')
        else
          SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end else
    Result := True;
end;

