param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Path
)

$ErrorActionPreference = "Stop"
& .\.venv\Scripts\python.exe -m cryox_chess migrate $Path
