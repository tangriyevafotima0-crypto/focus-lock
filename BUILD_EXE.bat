@echo off
setlocal EnableDelayedExpansion
title FocusLock v4.0 — Builder
color 0D
cls

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   FocusLock v4.0  —  UFQ Productivity System        ║
echo  ║   Focus + YouTube + Vault + AI + Rejalashtirish     ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ─── Python ──────────────────────────────────────────────
echo  [1/6]  Python...
python --version > "%TEMP%\fl_py.txt" 2>&1
if errorlevel 1 (
    echo  [XATO] Python topilmadi!
    echo  https://python.org/downloads → "Add Python to PATH" belgisini qo'ying
    start https://python.org/downloads
    pause & exit /b 1
)
set /p PY_VER=<"%TEMP%\fl_py.txt"
echo  [OK] %PY_VER%

:: ─── FocusLock.py ────────────────────────────────────────
echo.
echo  [2/6]  FocusLock.py tekshirilmoqda...
if not exist "%~dp0FocusLock.py" (
    echo  [XATO] FocusLock.py topilmadi! Bir papkada bo'lishi kerak.
    pause & exit /b 1
)
echo  [OK] FocusLock.py topildi

:: ─── Pip packages ────────────────────────────────────────
echo.
echo  [3/6]  Kerakli paketlar o'rnatilmoqda...
pip install pyinstaller yt-dlp --quiet --disable-pip-version-check
if errorlevel 1 (
    echo  [XATO] Paket o'rnatishda xato! Internet tekshiring.
    pause & exit /b 1
)
echo  [OK] pyinstaller + yt-dlp tayyor

:: ─── Build EXE ───────────────────────────────────────────
echo.
echo  [4/6]  EXE yaratilmoqda... (2-5 daqiqa, kuting)
echo.

cd /d "%~dp0"
if exist "build"          rmdir /s /q "build"
if exist "dist"           rmdir /s /q "dist"
if exist "FocusLock.spec" del /f /q "FocusLock.spec"

python -m PyInstaller --onefile --windowed --name "FocusLock" --clean --noconfirm FocusLock.py

if errorlevel 1 (
    echo.
    echo  [XATO] EXE yaratilmadi!
    echo  Yuqoridagi xabarni o'qing yoki fl_log.txt ni tekshiring.
    pause & exit /b 1
)

if not exist "dist\FocusLock.exe" (
    echo  [XATO] dist\FocusLock.exe topilmadi!
    pause & exit /b 1
)

copy /Y "dist\FocusLock.exe" "%~dp0FocusLock.exe" > nul
echo  [OK] FocusLock.exe yaratildi

:: ─── Cleanup ──────────────────────────────────────────────
rmdir /s /q "build"  > nul 2>&1
rmdir /s /q "dist"   > nul 2>&1
del /f /q "FocusLock.spec" > nul 2>&1

:: ─── Config ───────────────────────────────────────────────
echo.
echo  [5/6]  Config fayllar tekshirilmoqda...
if not exist "%~dp0fl_config.json" (
    echo  fl_config.json topilmadi — FocusLock o'zi yaratadi
) else (
    echo  [OK] fl_config.json bor
)

:: ─── Startup ──────────────────────────────────────────────
echo.
echo  [6/6]  Windows Startup...

set "EXE_FULL=%~dp0FocusLock.exe"
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" ^
    /v "FocusLock" /t REG_SZ /d "\"%EXE_FULL%\"" /f > nul 2>&1

if errorlevel 1 (
    echo  [OGOHLANTIRISH] Startup reestriga qo'shilmadi.
    echo  Qo'lda: Win+R → shell:startup → FocusLock.exe yorliq yarating
) else (
    echo  [OK] Startup qo'shildi: %EXE_FULL%
)

:: ─── Done ─────────────────────────────────────────────────
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║          ✅  MUVAFFAQIYATLI YARATILDI!               ║
echo  ╠══════════════════════════════════════════════════════╣
echo  ║                                                      ║
echo  ║  📁  Joylashuv:                                      ║
echo  ║      %~dp0FocusLock.exe
echo  ║                                                      ║
echo  ║  🔑  Asosiy parol:   UFQ2024                        ║
echo  ║  🔐  Vault paroli:   VAULT2024                      ║
echo  ║  🤖  AI uchun:       Vault → AI → ⚙ Sozlamalar     ║
echo  ║                      console.anthropic.com dan kalit║
echo  ║                                                      ║
echo  ║  ⚠   MUHIM: fl_config.json, fl_*.json, fl_*.enc    ║
echo  ║      fayllarini FocusLock.exe bilan BIR PAPKADA     ║
echo  ║      saqlang. Ko'chirmang!                           ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

explorer "%~dp0"
timeout /t 4 /nobreak > nul
start "" "%~dp0FocusLock.exe"
endlocal
