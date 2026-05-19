@echo off
chcp 65001 > nul
echo ================================================
echo   Construction de l'executable NewStyle
echo ================================================
echo.

REM Verifie que le venv existe
if not exist ".venv\Scripts\python.exe" (
    echo ERREUR: Le venv n'existe pas. Lancez d'abord run.bat une fois.
    pause
    exit /b 1
)

REM Installe PyInstaller dans le venv
echo [1/4] Installation de PyInstaller...
.venv\Scripts\pip.exe install pyinstaller --quiet
if errorlevel 1 (
    echo ERREUR: Impossible d'installer PyInstaller.
    pause
    exit /b 1
)

REM Nettoie les builds precedents
echo [2/4] Nettoyage des anciens builds...
if exist "dist\NewStyle" rmdir /s /q "dist\NewStyle"
if exist "build" rmdir /s /q "build"
if exist "NewStyle.spec" del "NewStyle.spec"

REM Construit l'executable
echo [3/4] Construction de l'executable (cela peut prendre 1-2 minutes)...
.venv\Scripts\pyinstaller.exe ^
    --onedir ^
    --windowed ^
    --name "NewStyle" ^
    --add-data "assets;assets" ^
    --add-data "data\schema.sql;data" ^
    --add-data "data\seed_data.sql;data" ^
    --hidden-import "bcrypt" ^
    --hidden-import "pygame" ^
    --noconfirm ^
    main.py

if errorlevel 1 (
    echo ERREUR: La construction a echoue. Relancez sans --windowed pour voir les erreurs.
    pause
    exit /b 1
)

REM Nettoie les fichiers temporaires
echo [4/4] Nettoyage des fichiers temporaires...
if exist "build" rmdir /s /q "build"
if exist "NewStyle.spec" del "NewStyle.spec"

echo.
echo ================================================
echo   SUCCES!
echo.
echo   L'executable se trouve dans:
echo     dist\NewStyle\NewStyle.exe
echo.
echo   Pour partager le jeu:
echo     Copiez le DOSSIER dist\NewStyle\ entier
echo     sur n'importe quelle machine Windows.
echo     (Pas besoin de Python, ni de git !)
echo ================================================
pause
