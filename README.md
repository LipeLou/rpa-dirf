# 🤖 Assistente EFD-REINF - Sistema Semi-Automático

Sistema para auxiliar no preenchimento de formulários EFD-REINF da Receita Federal.

## 🚀 Início Rápido

### Windows:
```bash
# Opção 1: Executar diretamente (RECOMENDADO)
.\executar.bat

# Opção 2: Ativar ambiente e executar
.\ativar_venv.bat
python automacao_efd.py

# Opção 3: Manual (se PowerShell bloquear)
venv\Scripts\activate.bat
python automacao_efd.py
```

**⚠️ IMPORTANTE:** No PowerShell, sempre use `.\` antes do nome do arquivo!

### Linux/Mac:
```bash
# Opção 1: Script automático
chmod +x ativar_venv.sh
./ativar_venv.sh

# Opção 2: Manual
source venv/bin/activate
python automacao_efd.py
```

## 📋 Pré-requisitos

- ✅ Python 3.13
- ✅ Chrome instalado
- ✅ Certificado digital (e-CPF ou e-CNPJ)
- ✅ Arquivo `dados.xlsx` com os dados a processar

## ⚡ Como Funciona

### Sistema PREENCHE automaticamente:
- **Processa TODOS os grupos** do Excel
- **Pula automaticamente** CPFs já lançados
- Data, CNPJ, CPF do Titular
- CPF e Relação de cada Dependente
- Planos de saúde e valores

### VOCÊ faz manualmente:
- Login (certificado digital)
- Navegação até o formulário
- **Sistema processa tudo automaticamente!**

### Sistema de Checkpoint:
- **Salva progresso** em banco SQLite
- **Permite pausar e retomar**
- **Evita reprocessar** CPFs já feitos
- **Relatórios detalhados** de progresso

## 📊 Velocidade

- **Manual puro:** ~5 min/grupo
- **Com assistente:** ~1.5 min/grupo ⚡
- **Economia:** ~70% de tempo

## 📊 Gerenciar Banco de Dados

### Executar Gerenciador de Checkpoint

**Windows:**
```bash
.\gerenciar_db.bat
```

**Ou manualmente:**
```bash
python gerenciar_checkpoint.py
```

### Funcionalidades do Gerenciador:

1. **📋 Ver status geral** - Resumo do banco de dados
2. **👤 Ver CPFs processados** - Lista todos os CPFs
3. **🔍 Buscar CPF específico** - Detalhes de um CPF
4. **📈 Ver estatísticas** - Análise detalhada
5. **🗑️ Limpar dados** - Limpar banco ou CPF específico
6. **📊 Exportar relatório** - Gerar Excel com todos os dados
7. **🔄 Resetar progresso** - Permitir reprocessar um CPF

## 📁 Estrutura

```
rpa-dirf/
├── automacao_efd.py        # Automação principal
├── gerenciar_checkpoint.py # Gerenciador de banco
├── dados.xlsx              # Planilha com dados
├── checkpoint_efd.db       # Banco de dados SQLite
├── requirements.txt        # Dependências
├── executar.bat           # Script Windows
├── gerenciar_db.bat       # Gerenciador Windows
└── venv/                  # Ambiente virtual
```

## 🔧 Configuração Inicial (Primeira Vez)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

**✅ Ambiente virtual já configurado!** Todas as dependências foram instaladas.

## 💡 Dica

O sistema usa um perfil dedicado do Chrome (`chrome_assistente/`) onde:
- Login fica salvo
- Certificado configurado
- Cookies persistem

Após primeira execução, login pode ser automático!

---

**Pronto para começar!** Execute `python automacao_efd.py` 🚀
