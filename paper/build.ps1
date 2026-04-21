param(
    [Parameter(Mandatory = $false)]
    [string]$Tex = "author.tex"
)

$paperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $paperDir

function Find-MiKTeXExecutable {
    param(
        [Parameter(Mandatory = $true)][string]$exeName
    )

    $cmd = Get-Command $exeName -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $candidateRoots = @(
        "C:\\Program Files\\MiKTeX",
        "C:\\Program Files (x86)\\MiKTeX",
        (Join-Path $env:LOCALAPPDATA "Programs\\MiKTeX"),
        (Join-Path $env:LOCALAPPDATA "MiKTeX"),
        (Join-Path $env:APPDATA "MiKTeX")
    )

    foreach ($root in $candidateRoots) {
        if (Test-Path $root) {
            $found = Get-ChildItem -Path $root -Filter $exeName -Recurse -ErrorAction SilentlyContinue |
                Select-Object -First 1 -ExpandProperty FullName
            if ($found) {
                return $found
            }
        }
    }

    return $null
}

$pdflatex = Find-MiKTeXExecutable -exeName "pdflatex.exe"
if (-not $pdflatex) {
    throw "pdflatex.exe not found. Install MiKTeX (or TeX Live) and try again."
}

$bibtex = Join-Path (Split-Path $pdflatex -Parent) "bibtex.exe"

Write-Host "Using pdflatex: $pdflatex"

& $pdflatex -interaction=nonstopmode -halt-on-error $Tex

$aux = [System.IO.Path]::ChangeExtension($Tex, "aux")
$job = [System.IO.Path]::GetFileNameWithoutExtension($Tex)

if ((Test-Path $aux) -and (Test-Path $bibtex)) {
    & $bibtex $job
}

& $pdflatex -interaction=nonstopmode -halt-on-error $Tex
& $pdflatex -interaction=nonstopmode -halt-on-error $Tex

Write-Host "Done. Output: $([System.IO.Path]::ChangeExtension($Tex, "pdf"))"