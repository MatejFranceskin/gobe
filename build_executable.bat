@echo off
echo Building MushroomCards executable...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build the executable using the .spec file (faster if it exists)
if exist "MushroomCards.spec" (
    echo Using existing MushroomCards.spec file for faster build...
    python -m PyInstaller MushroomCards.spec
) else (
    echo Creating new .spec file and building...
    python -m PyInstaller --onefile --windowed --name "MushroomCards" --add-data "gobe.db;." --add-data "arialuni.ttf;." cards_gui.py
)

REM Check if build was successful
if exist "dist\MushroomCards.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Files created in dist folder:
    dir "dist" /b
    echo.
    echo Executable size: 
    dir "dist\MushroomCards.exe" | find "MushroomCards.exe"
    echo.
    echo Ready for distribution! The executable is now self-contained
    echo and includes all required files ^(database and font^) bundled inside.
    echo.
    echo You can copy just the MushroomCards.exe file to any Windows
    echo computer and run it directly - no additional files needed!
    echo ========================================
    goto :end
) else (
    echo.
    echo BUILD FAILED!
    echo Check the output above for errors.
)

:end
pause
