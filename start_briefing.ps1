param(
    [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'

$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BaseDir

$DashboardUrl = "http://127.0.0.1:$Port/dashboard/index.html"
$LogDir = Join-Path $env:TEMP 'fire-weather-briefing'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Get-PreferredPython {
    $candidates = New-Object System.Collections.Generic.List[string]

    try {
        foreach ($candidate in @(where.exe python 2>$null)) {
            if ($candidate -and $candidate -notmatch 'WindowsApps') {
                $candidates.Add($candidate)
            }
        }
    }
    catch {
    }

    try {
        $pythonCmd = Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($pythonCmd -and $pythonCmd.Source -and $pythonCmd.Source -notmatch 'WindowsApps') {
            $candidates.Add($pythonCmd.Source)
        }
    }
    catch {
    }

    foreach ($knownPath in @(
        (Join-Path $env:LOCALAPPDATA 'miniconda3\python.exe'),
        (Join-Path $env:USERPROFILE 'miniconda3\python.exe'),
        (Join-Path $env:USERPROFILE 'anaconda3\python.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python311\python.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python310\python.exe')
    )) {
        if ($knownPath -and (Test-Path $knownPath)) {
            $candidates.Add($knownPath)
        }
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if ($candidate -and (Test-Path $candidate)) {
            return (Resolve-Path $candidate).Path
        }
    }

    $pyCmd = Get-Command py.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pyCmd) {
        try {
            $resolved = & $pyCmd.Source -3 -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $resolved -and (Test-Path $resolved.Trim())) {
                return (Resolve-Path $resolved.Trim()).Path
            }
        }
        catch {
        }
    }

    return $null
}

function Test-ServerReady {
    param(
        [string]$Url
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch {
        return $false
    }
}

$pythonExe = Get-PreferredPython
if (-not $pythonExe) {
    Write-Warning 'No working Python interpreter was found. Opening the static dashboard file instead.'
    Write-Warning 'If Python is installed, try launching from PowerShell after activating your Conda environment or adding Python to PATH.'
    Start-Process (Join-Path $BaseDir 'dashboard\index.html')
    exit 0
}

Write-Host "Using Python: $pythonExe"

$rssLog = Join-Path $LogDir 'rss_fetch.log'
$goesLog = Join-Path $LogDir 'goes_fetch.log'
$newsOutLog = Join-Path $LogDir 'news_refresh.out.log'
$newsErrLog = Join-Path $LogDir 'news_refresh.err.log'
$serverOutLog = Join-Path $LogDir 'server.out.log'
$serverErrLog = Join-Path $LogDir 'server.err.log'

try {
    & $pythonExe 'scripts\fetch_rss.py' *> $rssLog
}
catch {
    $_ | Out-File -FilePath $rssLog -Encoding utf8 -Append
}

try {
    & $pythonExe 'scripts\fetch_goes_page.py' *> $goesLog
}
catch {
    $_ | Out-File -FilePath $goesLog -Encoding utf8 -Append
}

try {
    Start-Process -FilePath $pythonExe -ArgumentList 'scripts\refresh_news_loop.py' -WorkingDirectory $BaseDir -WindowStyle Minimized -RedirectStandardOutput $newsOutLog -RedirectStandardError $newsErrLog | Out-Null
}
catch {
    $_ | Out-File -FilePath $newsErrLog -Encoding utf8 -Append
}

if (-not (Test-ServerReady -Url $DashboardUrl)) {
    try {
        Start-Process -FilePath $pythonExe -ArgumentList 'scripts\server.py', $Port -WorkingDirectory $BaseDir -WindowStyle Minimized -RedirectStandardOutput $serverOutLog -RedirectStandardError $serverErrLog | Out-Null
    }
    catch {
        $_ | Out-File -FilePath $serverErrLog -Encoding utf8 -Append
    }
}

Write-Host "Waiting for local server on port $Port..."
$ready = $false
for ($attempt = 1; $attempt -le 20; $attempt++) {
    if (Test-ServerReady -Url $DashboardUrl) {
        $ready = $true
        break
    }

    Start-Sleep -Seconds 1
}

if (-not $ready) {
    Write-Warning "Server did not respond after 20 seconds. Check $serverErrLog and $serverOutLog for details."
}

Start-Process $DashboardUrl
exit 0
