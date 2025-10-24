@echo off
echo ========================================
echo   ATIVANDO AMBIENTE VIRTUAL
echo ========================================
echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
echo ✅ Ambiente virtual ativado!
echo.
echo Para executar a automação:
echo   python automacao_efd.py
echo.
echo Para desativar o ambiente:
echo   deactivate
echo.
cmd /k
