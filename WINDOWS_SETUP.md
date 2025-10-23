# 🪟 Configuração Windows - RPA DIRF

## ✅ Problema Resolvido

O projeto foi migrado de Linux para Windows. Todas as configurações foram ajustadas automaticamente.

## 📋 O que foi corrigido:

1. **Ambiente Virtual**: Recriado para Windows
2. **Dependências**: Instaladas corretamente (Flask, Selenium, Pandas, OpenPyxl, etc.)
3. **ChromeDriver**: Configurado para usar Selenium Manager (automático)
4. **Encoding UTF-8**: Configurado para exibir emojis corretamente no PowerShell
5. **Detecção de SO**: Script detecta automaticamente Linux/Windows

## 🚀 Como executar:

### Opção 1: PowerShell (Recomendado)
```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Executar o script principal
python test_ecac.py

# Ou executar a aplicação web
python app.py
```

### Opção 2: Diretamente
```powershell
.\venv\Scripts\python.exe test_ecac.py
```

### Opção 3: Git Bash
```bash
source venv/Scripts/activate
python test_ecac.py
```

## 📦 Dependências instaladas:

- Flask 3.0.0
- Selenium 4.15.2
- Pandas 2.3.3
- OpenPyxl 3.1.5
- Webdriver-manager 4.0.1 (backup)

## 🔧 Configurações do Chrome:

- O Selenium Manager gerencia automaticamente o ChromeDriver
- Chrome deve estar instalado em: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Versão detectada: Chrome 141.0.7390.108

## ⚠️ Notas importantes:

1. **Primeira execução**: Selenium Manager vai baixar o ChromeDriver automaticamente
2. **Internet necessária**: Na primeira vez, precisa de internet para baixar o driver
3. **Encoding**: UTF-8 configurado automaticamente para Windows
4. **Excel**: O arquivo `dados.xlsx` deve estar na raiz do projeto

## 🐛 Solução de problemas:

### Chrome não abre:
- Verifique se o Chrome está instalado
- Reinstale o Chrome se necessário

### Erro de encoding:
- Já está corrigido! O script configura UTF-8 automaticamente

### Erro de módulo não encontrado:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📞 Suporte:

Se encontrar problemas, verifique:
1. Chrome está instalado?
2. Ambiente virtual está ativado?
3. Todas as dependências estão instaladas?

---
**Sistema testado**: Windows 10/11 com Python 3.13.9

