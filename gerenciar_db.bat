@echo off
echo ========================================
echo   GERENCIADOR DE CHECKPOINT EFD-REINF
echo ========================================
echo.

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erro ao ativar ambiente virtual.
    pause
    exit /b %ERRORLEVEL%
)
echo ✅ Ambiente virtual ativado!
echo.

echo 🚀 Iniciando gerenciador...
python gerenciar_checkpoint.py
echo.

echo ⏸️ Pressione qualquer tecla para sair...
pause
