# 🤖 Automação EFD-REINF

> Sistema completo para automatizar o preenchimento de declarações de imposto de renda (plano de saúde) da Receita Federal com assinatura eletrônica automática.

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.15.2-green.svg)](https://selenium.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


## 🚀 Características

- ✅ **100% Automático** - Assinatura eletrônica automatizada
- ✅ **Sistema de Checkpoints** - Retoma de onde parou
- ✅ **Gestão Inteligente** - Pula CPFs já processados e grupos sem valor
- ✅ **Validação Automática** - Ignora titulares/dependentes sem plano ativo
- ✅ **Tratamento de Erros** - Registra erros no checkpoint para análise
- ✅ **Relatórios Detalhados** - Acompanhamento completo


## 📋 Pré-requisitos

- Python 3.13+
- Google Chrome
- Assinador Serpro (ou equivalente)


## ⚡ Instalação

### Windows
```bash
# Execução rápida
.\executar.bat

# Ou passo a passo
.\ativar_venv.bat
python automacao_efd.py
```

### Linux/Mac
```bash
chmod +x ativar_venv.sh
./ativar_venv.sh
python automacao_efd.py
```


## 🎯 Como Usar

1. **Configure** os dados da empresa no `config.py`
2. **Adicione** a planilha `dados.xlsx` com os CPFs
3. **Execute** o sistema
4. **Faça login** manual no site da Receita (apenas uma vez)
5. **Aguarde** o processamento automático

### Fluxo Automático
```
📂 Lê Excel → 🌐 Abre Chrome → 🔐 Login Manual → 🤖 Processa Todos → 📊 Gera Relatórios
```


## ⚙️ Configuração

Edite o `config.py`:

```python
# Dados da empresa
PERIODO_APURACAO = "00/0000"
CNPJ_EMPRESA = "00.000.000/0000-00"
CNPJ_OPERADORA_PADRAO = "00.000.000/0000-00"

# Comportamento
VERIFICACAO_MANUAL_PADRAO = False    # True = pausa para revisar
METODO_ASSINATURA_PADRAO = 2         # 1=Apenas teclado, 2=Mouse + teclado
CHROME_VERSION = 141                  # Versão do Chrome instalada
```


## 🔐 Métodos de Assinatura

### Método A - Teclado
```
Sequência: ↑ + ↑ + Enter
```

### Método B - Mouse + Teclado
```
Sequência: Click(x,y) + Enter
```
> Requer configuração de coordenadas após login no ECAC


## 📋 Formato da Planilha

**Arquivo:** `dados.xlsx` **| Aba:** `MÊS 2025` (configurável em `config.py`)

| NOME | CPF | DEPENDENCIA | VALOR |
|------|-----|-------------|-------|
| João Silva | 000.000.000-00 | TITULAR | 150,00 |
| Maria Silva | 111.111.111-11 | ESPOSA | 150,00 |


## 📊 Gerenciar Progresso

```bash
# Windows
.\gerenciar_db.bat

# Linux/Mac  
python gerenciar_checkpoint.py
```

**Funcionalidades disponíveis:**
- Ver status geral e estatísticas
- Buscar CPFs específicos
- Limpar dados e resetar progresso
- Exportar relatórios em Excel
- Alterar checkpoint atual
- Visualizar grupos com erro ou pulados


## 📁 Estrutura do Projeto

```
rpa-dirf/
├── automacao_efd.py        # Automação principal
├── gerenciar_checkpoint.py # Gerenciador de progresso  
├── config.py               # Configurações
├── dados.xlsx              # Planilha com dados
├── requirements.txt        # Dependências
├── executar.bat           # Script Windows
└── gerenciar_db.bat       # Gerenciador Windows
```


## 🛡️ Segurança

- **🔒 FAILSAFE**: Mover mouse para canto superior esquerdo cancela tudo
- **👤 Login manual**: Certificado digital sempre requer interação manual
- **💾 Dados locais**: Todas as informações permanecem no seu computador


## ❓ Problemas Comuns

| Problema | Solução |
|----------|---------|
| Erro de assinatura | Verificar se Assinador Serpro está rodando |
| CPF não encontrado | Verificar formato da planilha Excel |
| Certificado não funciona | Fazer login manual no navegador normal primeiro |
| Erro de versão ChromeDriver | Atualizar `CHROME_VERSION` no `config.py` com sua versão do Chrome |


## 🔄 Dependências

```txt
selenium==4.15.2
selenium-stealth>=1.0.6
pandas==2.3.3
openpyxl==3.1.5
undetected-chromedriver==3.5.5
PyAutoGUI==0.9.54
Pillow>=10.0.0
```


## 📞 Suporte

1. Verificar logs no terminal
2. Consultar checkpoints no gerenciador
3. Analisar relatórios gerados
4. Resetar progresso se necessário

---

**🎯 Sistema pronto para produção | ⚡ 100% automático | 📊 Relatórios inteligentes**
