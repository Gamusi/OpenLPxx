; Inno Setup Script for OpenLP 3.1.7 (Anglican Offline Distribution)
; Task 6.2 — Fresh Installations Only (preserves any existing user data directory untouched)

#define MyAppName "OpenLP"
#define MyAppVersion "3.1.7"
#define MyAppPublisher "OpenLP Developers"
#define MyAppURL "https://openlp.org/"
#define MyAppExeName "OpenLP.exe"
#define BuildRoot "D:\OpenLPxx\distribution\app-build\OpenLP"
#define StagingRoot "D:\OpenLPxx\distribution\content-staging"

[Setup]
AppId={{8F9E2B61-5D4C-4A31-9B7E-3170A6E1C062}
AppName=OpenLP
AppVersion=3.1.7
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\OpenLP Anglican
DefaultGroupName=OpenLP Anglican
UninstallDisplayName=OpenLP 3.1.7 (Anglican Distribution)
AllowNoIcons=yes
LicenseFile={#BuildRoot}\LICENSE.txt
SetupIconFile={#BuildRoot}\OpenLP.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog commandline
OutputDir=D:\OpenLPxx\distribution\installer
OutputBaseFilename=OpenLP-3.1.7-Anglican-Setup
Compression=lzma2/fast
SolidCompression=no
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 1. Standalone OpenLP 3.1.7 Application & Runtime (Python 3.11, PyQt5, QtWebEngine, VLC)
Source: "{#BuildRoot}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 2. Reference copy of Service Templates inside application directory
Source: "{#StagingRoot}\service-templates\*.osz"; DestDir: "{app}\service-templates"; Flags: ignoreversion

; 3. Preconfigured User Data Profile (ONLY initialized on a fresh profile; never overwrites existing data)
Source: "{#StagingRoot}\Data\*"; DestDir: "{code:GetProfileDir}\Data"; Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs createallsubdirs; Check: ShouldInitializeUserData
Source: "{#StagingRoot}\Data\bibles\*.sqlite"; DestDir: "{code:GetProfileDir}\Data\bibles"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "{#StagingRoot}\service-templates\*.osz"; DestDir: "{code:GetProfileDir}\Service Templates"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--portable --portable-path ""{code:GetProfileDir}"""; WorkingDir: "{app}"; IconFilename: "{app}\OpenLP.ico"
Name: "{group}\Service Templates"; Filename: "{code:GetProfileDir}\Service Templates"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--portable --portable-path ""{code:GetProfileDir}"""; WorkingDir: "{app}"; IconFilename: "{app}\OpenLP.ico"; Tasks: desktopicon

[Code]
var
  ProfileChecked: Boolean;
  AllowInitData: Boolean;

function GetProfileDir(Param: String): String;
var
  CustomPath: String;
begin
  CustomPath := ExpandConstant('{param:DATAPATH|}');
  if CustomPath <> '' then
    Result := CustomPath
  else
    Result := ExpandConstant('{userappdata}\OpenLP-Anglican');
end;

function ShouldInitializeUserData(): Boolean;
var
  ProfDir: String;
begin
  if not ProfileChecked then
  begin
    ProfDir := GetProfileDir('');
    if DirExists(ProfDir + '\Data') or FileExists(ProfDir + '\Data\OpenLP.ini') then
    begin
      Log('Existing OpenLP user profile detected at ' + ProfDir + '\Data; preserving user databases and settings unchanged during upgrade.');
      AllowInitData := False;
    end
    else
    begin
      Log('Fresh OpenLP user profile at ' + ProfDir + '\Data; initializing standard content.');
      AllowInitData := True;
    end;
    ProfileChecked := True;
  end;
  Result := AllowInitData;
end;
