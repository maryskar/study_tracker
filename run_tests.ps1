$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python не найден в PATH. Установите Python 3.10+ и повторите запуск."
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m pip install -r requirements-dev.txt
    python -m pytest
} else {
    py -m pip install -r requirements-dev.txt
    py -m pytest
}
