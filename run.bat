@echo off
chcp 65001 > nul

REM Si le venv n'existe pas, le creer et installer les dependances
if not exist ".venv\Scripts\python.exe" (
    echo Configuration initiale - veuillez patienter...

    python --version > nul 2>&1
    if errorlevel 1 (
        echo ERREUR: Python n'est pas installe.
        echo Telechargez-le sur https://www.python.org
        pause
        exit /b 1
    )

    python -m venv .venv
    .venv\Scripts\pip.exe install -r requirements.txt --quiet
    echo Configuration terminee!
    echo.
)

.venv\Scripts\python.exe main.py
