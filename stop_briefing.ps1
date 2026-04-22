param(
    [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'

$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LockPath = Join-Path $BaseDir 'data\news_refresh.lock'
$stopped = New-Object System.Collections.Generic.List[string]

$targets = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and
    $_.Name -match '^python(?:w)?\.exe$' -and
    (
        $_.CommandLine -match [regex]::Escape("http.server $Port") -or
        $_.CommandLine -match 'server\.py' -or
        $_.CommandLine -match 'refresh_news_loop\.py'
    )
}

foreach ($process in $targets) {
    try {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
        $stopped.Add("Stopped PID $($process.ProcessId): $($process.CommandLine)")
    }
    catch {
        Write-Warning "Could not stop PID $($process.ProcessId): $($_.Exception.Message)"
    }
}

if (Test-Path $LockPath) {
    Remove-Item $LockPath -Force -ErrorAction SilentlyContinue
}

if ($stopped.Count -gt 0) {
    Write-Host 'Stopped briefing background processes:'
    $stopped | ForEach-Object { Write-Host "- $_" }
}
else {
    Write-Host 'No matching briefing background processes were running.'
}

Write-Host "Cleared lock file: $LockPath"
exit 0
