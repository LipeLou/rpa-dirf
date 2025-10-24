@echo off
echo ========================================
echo   EXECUTANDO AUTOMAÇÃO EFD-REINF
echo ========================================
echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
echo ✅ Ambiente virtual ativado!
echo.
echo 🚀 Iniciando automação...
echo.
python automacao_efd.py
echo.
echo ⏸️ Pressione qualquer tecla para sair...
pause >nul
