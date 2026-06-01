# pdfocr Install Fallback

Use this when `pdfocr` is missing or fails to start.

Install only under the user's home directory, never inside the current
workspace.

Supported release assets:
- Linux `x86_64`
- macOS `arm64`
- Windows `x86_64`

## Linux x86_64

```bash
set -euo pipefail
mkdir -p "$HOME/.local/opt/pdfocr" "$HOME/.local/bin"
curl -fsSL -o "$HOME/.local/opt/pdfocr/pdfocr.tar.gz" \
  "https://github.com/planetis-m/pdfocr/releases/latest/download/pdfocr-linux-x86_64.tar.gz"
rm -rf "$HOME/.local/opt/pdfocr/current"
mkdir -p "$HOME/.local/opt/pdfocr/current"
tar -xzf "$HOME/.local/opt/pdfocr/pdfocr.tar.gz" -C "$HOME/.local/opt/pdfocr/current"
ln -sfn "$HOME/.local/opt/pdfocr/current/pdfocr" "$HOME/.local/bin/pdfocr"
export PATH="$HOME/.local/bin:$PATH"
pdfocr --help >/dev/null
```

## macOS arm64

```bash
set -euo pipefail
mkdir -p "$HOME/.local/opt/pdfocr" "$HOME/.local/bin"
curl -fsSL -o "$HOME/.local/opt/pdfocr/pdfocr.tar.gz" \
  "https://github.com/planetis-m/pdfocr/releases/latest/download/pdfocr-macos-arm64.tar.gz"
rm -rf "$HOME/.local/opt/pdfocr/current"
mkdir -p "$HOME/.local/opt/pdfocr/current"
tar -xzf "$HOME/.local/opt/pdfocr/pdfocr.tar.gz" -C "$HOME/.local/opt/pdfocr/current"
ln -sfn "$HOME/.local/opt/pdfocr/current/pdfocr" "$HOME/.local/bin/pdfocr"
export PATH="$HOME/.local/bin:$PATH"
pdfocr --help >/dev/null
```

## Windows x86_64 (PowerShell)

```powershell
$ErrorActionPreference = "Stop"
$dst = "$HOME\.local\opt\pdfocr"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
$zip = Join-Path $env:TEMP "pdfocr.zip"
Invoke-WebRequest -Uri "https://github.com/planetis-m/pdfocr/releases/latest/download/pdfocr-windows-x86_64.zip" -OutFile $zip
Remove-Item -Recurse -Force (Join-Path $dst "current") -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $dst "current") | Out-Null
Expand-Archive -Path $zip -DestinationPath (Join-Path $dst "current") -Force
$exe = Get-ChildItem -Path (Join-Path $dst "current") -Recurse -Filter "pdfocr.exe" | Select-Object -First 1
$exeDir = Split-Path -Parent $exe.FullName
$env:Path = "$exeDir;$env:Path"
pdfocr --help | Out-Null
```

## API Key Setup

After installation, tell the user to configure a DeepInfra API key before
running OCR.

Recommended environment variable:
- Linux/macOS: `export DEEPINFRA_API_KEY="your_api_key"`
- Windows PowerShell: `$env:DEEPINFRA_API_KEY = "your_api_key"`

Alternatively, create `config.json` beside the real binary, for example in
`~/.local/opt/pdfocr/current/`:

```json
{
  "api_key": "your_deepinfra_api_key"
}
```

## Notes

- Keep the extracted runtime files with the real binary. Do not copy only
  `pdfocr` or `pdfocr.exe` elsewhere.
- If installation fails because of permission or sandbox restrictions, request escalated permission and retry.
- If platform/architecture is unsupported, stop and ask the user for manual installation steps.
