# Requires: PowerShell 5.1+; Pester 5+
$ErrorActionPreference = 'Stop'

# Ensure Pester v5 (user scope)
if (-not (Get-Module -ListAvailable -Name Pester | Where-Object { $_.Version.Major -ge 5 })) {
  try {
    Set-PSRepository PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue
  } catch {}
  Install-Module Pester -MinimumVersion 5.5 -Scope CurrentUser -Force -SkipPublisherCheck
}
Import-Module Pester -MinimumVersion 5.5 -Force

$IsWindows = $PSVersionTable.Platform -eq 'Win32NT'
$repo = (Resolve-Path "$PSScriptRoot\..").Path
$python = "python"

# test sandbox
$dir = Join-Path $env:TEMP "nano_test_ps"
Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $dir | Out-Null

"hello one"    | Set-Content "$dir\a.txt"
"hidden stuff" | Set-Content "$dir\desktop.ini"
attrib +h +s "$dir\desktop.ini" | Out-Null
"dot secret"   | Set-Content "$dir\.secret.txt"
New-Item -ItemType Directory -Path "$dir\hidden_dir" | Out-Null
"secret"       | Set-Content "$dir\hidden_dir\b.txt"
attrib +h +s "$dir\hidden_dir" | Out-Null

Describe 'Hidden semantics vs PowerShell' {
  It 'GCI counts (no -Force) == 2' -Skip:(-not $IsWindows) {
    ((Get-ChildItem $dir -Recurse | Measure-Object).Count) | Should -Be 2
  }

  It 'GCI counts (-Force) == 5' -Skip:(-not $IsWindows) {
    ((Get-ChildItem $dir -Recurse -Force | Measure-Object).Count) | Should -Be 5
  }

  It 'nano.py --ingest-skip-hidden total_considered == 2 on Windows' -Skip:(-not $IsWindows) {
    $root = Join-Path $repo 'nroot'
    $json = & $python "$repo\nano.py" --ingest-dir "$dir" --ingest-skip-hidden --ingest-exts= --root-dir "$root"
    $first = $json.IndexOf('{'); $last = $json.LastIndexOf('}')
    $blob = $json.Substring($first, $last - $first + 1)
    ($blob | ConvertFrom-Json).total_considered | Should -Be 2
  }

  It 'nano.py without skip sees 4 files' -Skip:(-not $IsWindows) {
    $root = Join-Path $repo 'nroot2'
    $json = & $python "$repo\nano.py" --ingest-dir "$dir" --ingest-exts= --root-dir "$root"
    $first = $json.IndexOf('{'); $last = $json.LastIndexOf('}')
    $blob = $json.Substring($first, $last - $first + 1)
    ($blob | ConvertFrom-Json).total_considered | Should -Be 4
  }
}
