@echo off
echo ========================================
echo   EXECUTANDO AUTOMACAO EFD-REINF
echo ========================================
echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
echo Ambiente virtual ativado!
echo.
echo Iniciando automacao...
echo.
python automacao_efd.py
echo.
pause
