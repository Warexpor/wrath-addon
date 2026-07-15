# Install Wrath addon into Grok Build (reinstall + absolute MCP path patch)
param(
    [switch]$Rules,
    [switch]$NoTrust
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Grok = Join-Path $env:USERPROFILE ".grok\bin\grok.exe"
if (-not (Test-Path $Grok)) {
    $cmd = Get-Command grok -ErrorAction SilentlyContinue
    if ($cmd) { $Grok = $cmd.Source } else { throw "grok CLI not found" }
}

Write-Host "Validating plugin at $Root ..."
& $Grok plugin validate $Root
if ($LASTEXITCODE -ne 0) { throw "validate failed: $LASTEXITCODE" }

$trust = @()
if (-not $NoTrust) { $trust = @("--trust") }

Write-Host "Installing (trust=$([bool]-not $NoTrust)) ..."
# Local installs copy files; refresh by uninstall then install.
& $Grok plugin uninstall wrath --confirm 2>$null
& $Grok plugin install $Root @trust
if ($LASTEXITCODE -ne 0) { throw "install failed: $LASTEXITCODE" }

# Patch installed .mcp.json with absolute path — Grok may start MCP with cwd != plugin root.
$registry = Join-Path $env:USERPROFILE ".grok\installed-plugins\registry.json"
$installed = $null
if (Test-Path $registry) {
    $reg = Get-Content $registry -Raw | ConvertFrom-Json
    foreach ($prop in $reg.repos.PSObject.Properties) {
        $repo = $prop.Value
        if ($repo.plugins.wrath) {
            $installed = $repo.path
            break
        }
    }
}
if (-not $installed) {
    $candidates = Get-ChildItem (Join-Path $env:USERPROFILE ".grok\installed-plugins") -Directory -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName "mcp\run.py") }
    if ($candidates) { $installed = $candidates[0].FullName }
}

if ($installed) {
    $runPy = Join-Path $installed "mcp\run.py"
    if (Test-Path $runPy) {
        $mcpObj = @{
            mcpServers = @{
                wrath = @{
                    command = "python"
                    args    = @($runPy)
                }
            }
        }
        $mcpPath = Join-Path $installed ".mcp.json"
        ($mcpObj | ConvertTo-Json -Depth 6) | Set-Content -Path $mcpPath -Encoding utf8
        Write-Host "Patched MCP absolute path -> $runPy"
    }
} else {
    Write-Host "WARN: could not locate installed plugin to patch MCP path" -ForegroundColor Yellow
}

if ($Rules) {
    $rulesDir = Join-Path $env:USERPROFILE ".grok\rules"
    New-Item -ItemType Directory -Force -Path $rulesDir | Out-Null
    Copy-Item (Join-Path $Root "rules\WRATH.md") (Join-Path $rulesDir "wrath.md") -Force
    Write-Host "Copied rules -> $rulesDir\wrath.md"
}

Write-Host ""
Write-Host "Done. Next:"
Write-Host "  - Restart grok or reload plugins (Plugins tab: r)"
Write-Host "  - Try /wrath  /wrath-status  /wrath-thin  /wrath-check  /wrath-review"
Write-Host "  - Overrides: WRATH_ALLOW_FORCE / HARD / CLEAN / PIPE_EXEC ; WRATH_STRICT=1"
& $Grok plugin details wrath 2>$null
if ($LASTEXITCODE -ne 0) { & $Grok plugin list }
