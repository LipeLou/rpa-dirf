# 🤖 Assistente EFD-REINF - Sistema Semi-Automático

Sistema para auxiliar no preenchimento de formulários EFD-REINF da Receita Federal.

## 🚀 Início Rápido

```bash
# 1. Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# 2. Executar assistente
python main.py
```

## 📋 Pré-requisitos

- ✅ Python 3.13
- ✅ Chrome instalado
- ✅ Certificado digital (e-CPF ou e-CNPJ)
- ✅ Arquivo `dados.xlsx` com os dados a processar

## ⚡ Como Funciona

### Sistema PREENCHE automaticamente:
- Data, CNPJ, CPF do Titular
- CPF e Relação de cada Dependente

### VOCÊ faz manualmente:
- Login (certificado digital)
- Navegação entre formulários
- Adição de planos de saúde e valores
- **Revisão e ENVIO** (controle total!)

## 📊 Velocidade

- **Manual puro:** ~5 min/grupo
- **Com assistente:** ~1.5 min/grupo ⚡
- **Economia:** ~70% de tempo

## 📁 Estrutura

```
rpa-dirf/
├── main.py              # Assistente principal (USE ESTE)
├── dados.xlsx           # Planilha com dados
├── requirements.txt     # Dependências
├── app.py              # Servidor Flask (opcional)
├── gerenciar_db.py     # Gerenciador de BD (opcional)
└── venv/               # Ambiente virtual
```

## 🔧 Configuração Inicial (Primeira Vez)

```bash
# Criar ambiente virtual
py -m venv venv

# Ativar
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

## 💡 Dica

O sistema usa um perfil dedicado do Chrome (`chrome_assistente/`) onde:
- Login fica salvo
- Certificado configurado
- Cookies persistem

Após primeira execução, login pode ser automático!

---

**Pronto para começar!** Execute `python main.py` 🚀
