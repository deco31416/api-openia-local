# ChatGPT Web Bridge - Script de arranque rápido
param(
    [int]$Port = 9090,
    [switch]$Visible = $true
)

$venvPython = "c:\Users\HP\Desktop\idea-loca\.venv\Scripts\python.exe"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  ChatGPT Web Bridge - Arranque" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Puerto: $Port"
Write-Host "  Modo:   $(if ($Visible) { 'VISIBLE (debug)' } else { 'INVISIBLE' })"
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

$args = @("server.py", "--port", $Port)
if (-not $Visible) {
    $args += "--no-headless"
}

& $venvPython $args
