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
    $pluginsRoot = Join-Path $env:USERPROFILE ".grok\installed-plugins"
    $candidates = Get-ChildItem $pluginsRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object {
            (Test-Path (Join-Path $_.FullName "mcp\run.py")) -and
            (Test-Path (Join-Path $_.FullName ".claude-plugin\plugin.json"))
        }
    foreach ($c in $candidates) {
        try {
            $man = Get-Content (Join-Path $c.FullName ".claude-plugin\plugin.json") -Raw | ConvertFrom-Json
            if ($man.name -eq "wrath") {
                $installed = $c.FullName
                break
            }
        } catch { }
    }
}

if ($installed) {
    $launchCmd = Join-Path $installed "mcp\launch.cmd"
    $runPy = Join-Path $installed "mcp\run.py"
    $launcher = if (Test-Path $launchCmd) { $launchCmd } elseif (Test-Path $runPy) { $runPy } else { $null }
    if ($launcher) {
        $mcpObj = [ordered]@{
            mcpServers = [ordered]@{
                wrath = [ordered]@{
                    command = $launcher
                    args    = @()
                }
            }
        }
        $mcpPath = Join-Path $installed ".mcp.json"
        $json = $mcpObj | ConvertTo-Json -Depth 6
        # UTF-8 without BOM (PowerShell 5 may only offer utf8 with BOM)
        [System.IO.File]::WriteAllText($mcpPath, $json + "`n")
        Write-Host "Patched MCP absolute launcher -> $launcher"
        # User config survives local-plugin sync (Grok may reset installed .mcp.json on restart).
        & $Grok mcp remove wrath --scope user 2>$null
        & $Grok mcp add wrath --scope user -- $launcher
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARN: grok mcp add wrath failed ($LASTEXITCODE)" -ForegroundColor Yellow
        } else {
            Write-Host "Registered wrath MCP in ~/.grok/config.toml"
        }
    }
    # Drop empty commands/ so Grok does not report a phantom command dir
    $cmdDir = Join-Path $installed "commands"
    if ((Test-Path $cmdDir) -and -not (Get-ChildItem $cmdDir -Force -ErrorAction SilentlyContinue | Select-Object -First 1)) {
        Remove-Item $cmdDir -Force -Recurse -ErrorAction SilentlyContinue
        Write-Host "Removed empty commands/ from install"
    }
} else {
    Write-Host "WARN: could not locate installed wrath plugin to patch MCP path" -ForegroundColor Yellow
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
Write-Host "  - Try /wrath  /wrath-status  /wrath-doctor  /wrath-profile  /wrath-yolo"
Write-Host "  - Workflows: /wrath-thin  /wrath-check  /wrath-ship  /wrath-why"
Write-Host "  - Overrides: WRATH_ALLOW_* ; WRATH_STRICT ; WRATH_PRIVACY ; WRATH_YOLO ; WRATH_ORCHESTRATE"
& $Grok plugin details wrath 2>$null
if ($LASTEXITCODE -ne 0) { & $Grok plugin list }
