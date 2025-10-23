#!/bin/bash

echo "================================================"
echo "🚀 SETUP - Projeto Selenium Formulário de DEVs"
echo "================================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 não encontrado. Por favor, instale Python 3 primeiro."
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"
echo ""

# Criar ambiente virtual (opcional)
read -p "Deseja criar um ambiente virtual? (s/n): " criar_venv
if [ "$criar_venv" = "s" ] || [ "$criar_venv" = "S" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual criado e ativado"
fi

# Instalar dependências
echo ""
echo "📦 Instalando dependências..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Verificar ChromeDriver
echo ""
echo "🔍 Verificando ChromeDriver..."
if ! command -v chromedriver &> /dev/null
then
    echo "⚠️  ChromeDriver não encontrado"
    echo ""
    echo "Para instalar o ChromeDriver:"
    echo "  Ubuntu/Debian: sudo apt-get install chromium-chromedriver"
    echo "  Ou baixe em: https://chromedriver.chromium.org/downloads"
    echo ""
else
    echo "✅ ChromeDriver encontrado: $(chromedriver --version)"
fi

echo ""
echo "================================================"
echo "✅ SETUP CONCLUÍDO!"
echo "================================================"
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Inicie o servidor Flask:"
echo "   python app.py"
echo ""
echo "2. Em outro terminal, execute os testes:"
echo "   python test_selenium.py"
echo ""
echo "3. Acesse no navegador:"
echo "   http://localhost:5000"
echo ""
echo "================================================"

