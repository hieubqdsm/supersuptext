# SuperSupText

A lightweight, fast text editor inspired by Sublime Text.

## Features

- ✅ Syntax highlighting (Python, JavaScript, C++, SQL, HTML, CSS, etc.)
- ✅ Multiple tabs
- ✅ File explorer sidebar
- ✅ Search and replace (with regex)
- ✅ Autosave (restores unsaved files on restart)
- ✅ Drag and drop file support
- ✅ Minimap
- ✅ Dark theme

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

---

## Build Executable (EXE)

```powershell
# Build single exe file
python build.py

# Output: dist/SuperSupText.exe
```

---

## Build Installer (MSI/Setup)

### Option 1: Inno Setup (Recommended)

1. **Download** [Inno Setup](https://jrsoftware.org/isdl.php) and install

2. **Build exe first:**
   ```powershell
   python build.py
   ```

3. **Create `installer.iss`:**
   ```iss
   [Setup]
   AppName=SuperSupText
   AppVersion=1.0.0
   DefaultDirName={autopf}\SuperSupText
   DefaultGroupName=SuperSupText
   OutputDir=installer
   OutputBaseFilename=SuperSupText-Setup
   Compression=lzma
   SolidCompression=yes
   
   [Files]
   Source: "dist\SuperSupText.exe"; DestDir: "{app}"; Flags: ignoreversion
   
   [Icons]
   Name: "{group}\SuperSupText"; Filename: "{app}\SuperSupText.exe"
   Name: "{autodesktop}\SuperSupText"; Filename: "{app}\SuperSupText.exe"
   
   [Registry]
   Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\SuperSupText.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\SuperSupText.exe"; Flags: uninsdeletekey
   ```

4. **Compile:** Open `installer.iss` with Inno Setup → Build → Compile

5. **Output:** `installer/SuperSupText-Setup.exe`

### Option 2: NSIS

Similar to Inno Setup, download from [nsis.sourceforge.io](https://nsis.sourceforge.io/)

---

## Add to Windows Search/App List

### Method 1: Start Menu Shortcut (Automatic via Installer)

If you use the Inno Setup installer above, it automatically creates Start Menu shortcuts.

### Method 2: Manual (Without Installer)

1. **Copy exe** to a permanent location:
   ```powershell
   mkdir "$env:LOCALAPPDATA\SuperSupText"
   copy dist\SuperSupText.exe "$env:LOCALAPPDATA\SuperSupText\"
   ```

2. **Create Start Menu shortcut:**
   ```powershell
   $WshShell = New-Object -ComObject WScript.Shell
   $Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\SuperSupText.lnk")
   $Shortcut.TargetPath = "$env:LOCALAPPDATA\SuperSupText\SuperSupText.exe"
   $Shortcut.Save()
   ```

3. **Now searchable!** Press `Win` key and type "SuperSupText"

### Method 3: Register in App Paths (Requires Admin)

```powershell
# Run as Administrator
$exePath = "C:\Path\To\SuperSupText.exe"
New-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\SuperSupText.exe" -Force
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\SuperSupText.exe" -Name "(Default)" -Value $exePath
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+W | Close tab |
| Ctrl+F | Find |
| Ctrl+H | Replace |
| Ctrl+G | Go to line |
| Ctrl+B | Toggle sidebar |
| Ctrl+/ | Toggle comment |

---

## License

MIT
