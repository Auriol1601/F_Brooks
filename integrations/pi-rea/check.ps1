# Verifie que l'integration REA <-> pi est en place et conforme a la reference versionnee.
# Usage : powershell -File integrations/pi-rea/check.ps1

$reference = Join-Path $PSScriptRoot "mcp.json"
$live = Join-Path $env:USERPROFILE ".pi\agent\mcp.json"

Write-Output "== Versions"
Write-Output ("pi  " + (pi --version))
Write-Output ("rea " + (rea --version))

Write-Output "== Configuration ~/.pi/agent/mcp.json"
if (-not (Test-Path $live)) {
    Write-Output "ABSENTE : lancer 'rea setup --client pi --yes'"
    exit 1
}
$refRea = (Get-Content $reference -Raw | ConvertFrom-Json).mcpServers.rea | ConvertTo-Json -Depth 5
$liveRea = (Get-Content $live -Raw | ConvertFrom-Json).mcpServers.rea | ConvertTo-Json -Depth 5
if ($refRea -eq $liveRea) {
    Write-Output "Entree 'rea' conforme a la reference"
} else {
    Write-Output "Entree 'rea' differente de la reference :"
    Write-Output $liveRea
}

Write-Output "== rea doctor"
$doctor = rea doctor --client pi --json | ConvertFrom-Json
Write-Output ("healthy: " + $doctor.healthy)

Write-Output "== pi mcp list"
$list = pi mcp list
$status = $LASTEXITCODE
$list | Where-Object { $_ -match '^rea:' }
exit $status
