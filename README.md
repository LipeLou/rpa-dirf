# 🤖 Automação EFD-REINF - Sistema 100% Automático

Sistema completo para automatizar o preenchimento de formulários EFD-REINF da Receita Federal com assinatura eletrônica automática.

## 🚀 Características Principais

- ✅ **100% Automático** - Assinatura eletrônica automatizada
- ✅ **Sistema de Checkpoints** - Retoma de onde parou
- ✅ **Duplo Método de Assinatura** - Compatível com diferentes sistemas
- ✅ **Interface Simplificada** - Terminal limpo e direto
- ✅ **Gestão Inteligente** - Pula CPFs já processados automaticamente
- ✅ **Relatórios Detalhados** - Acompanhamento completo do progresso

## 📋 Pré-requisitos

- ✅ **Python 3.13+**
- ✅ **Chrome** instalado
- ✅ **Certificado digital** (e-CPF ou e-CNPJ)
- ✅ **Assinador Serpro** ou equivalente
- ✅ **Arquivo Excel** com dados (`dados.xlsx`)

## ⚡ Instalação e Execução

### Windows (Recomendado):
```bash
# Execução rápida
.\executar.bat

# Ou manual
.\ativar_venv.bat
python automacao_efd.py
```

### Linux/Mac:
```bash
# Dar permissão
chmod +x ativar_venv.sh

# Executar
./ativar_venv.sh
python automacao_efd.py
```

## 🎛️ Configuração Inicial

Ao executar, o sistema perguntará:

### 1. 🔍 Verificação Manual de Dados
- **S** - Pausa para revisão antes de cada envio
- **N** - Processamento totalmente automático ⚡

### 2. 🔐 Método de Assinatura
- **1** - **Método A**: Seta ↑ → Seta ↑ → Enter
- **2** - **Método B**: Click do Mouse + Enter

### 3. 🎯 Coordenadas (apenas Método B)
- **1** - Detectar posição atual do mouse
- **2** - Inserir coordenadas manualmente
- **3** - Usar coordenadas salvas

## 📊 Como Funciona

### 🎯 Fluxo Automático:
1. **📂 Lê dados** do Excel (`dados.xlsx`, planilha `MAR 2025`)
2. **🌐 Abre Chrome** com perfil dedicado
3. **🔐 Aguarda login** manual no site da Receita
4. **🤖 Processa TODOS** os grupos automaticamente:
   - Preenche dados do titular
   - Adiciona dependentes
   - Inclui planos de saúde
   - **📤 Envia declaração**
   - **🔐 Assina eletronicamente** (automático!)
   - **➡️ Vai para próximo CPF**
5. **📊 Gera relatórios** de progresso

### 💾 Sistema de Checkpoints:
- Salva progresso em `checkpoint_efd.db`
- Permite pausar e retomar a qualquer momento
- Pula automaticamente CPFs já processados
- Rastreia erros e sucessos

## 📊 Gerenciar Progresso

```bash
# Windows
.\gerenciar_db.bat

# Linux/Mac
python gerenciar_checkpoint.py
```

### Funcionalidades do Gerenciador:
1. **📋 Ver status geral** - Resumo do progresso
2. **👤 Ver CPFs processados** - Lista detalhada
3. **🔍 Buscar CPF específico** - Detalhes individuais
4. **📈 Ver estatísticas** - Análise completa
5. **🗑️ Limpar dados** - Reset do banco
6. **📊 Exportar relatório** - Excel com todos os dados
7. **🔄 Resetar progresso** - Reprocessar CPF específico
8. **📈 Gerar visualização** - Planilha de acompanhamento
9. **🎯 Ver checkpoint atual** - Status atual
10. **⚙️ Alterar checkpoint** - Mudar posição atual

## 📁 Estrutura do Projeto

```
rpa-dirf/
├── automacao_efd.py        # 🤖 Automação principal
├── gerenciar_checkpoint.py # 📊 Gerenciador de progresso
├── config.py               # ⚙️ Configurações do sistema
├── dados.xlsx              # 📋 Planilha com dados
├── checkpoint_efd.db       # 💾 Banco de checkpoints
├── requirements.txt        # 📦 Dependências
├── executar.bat           # 🚀 Script Windows
├── gerenciar_db.bat       # 📊 Gerenciador Windows
├── ativar_venv.bat        # ⚙️ Ativador Windows
├── ativar_venv.sh         # ⚙️ Ativador Linux/Mac
├── venv/                  # 🐍 Ambiente virtual
└── chrome_efd/            # 🌐 Perfil Chrome dedicado
```

## 🔧 Dependências

```txt
Flask==3.0.0
selenium==4.15.2
pandas==2.3.3
openpyxl==3.1.5
webdriver-manager==4.0.1
undetected-chromedriver==3.5.5
selenium-stealth==1.0.6
PyAutoGUI==0.9.54
Pillow>=10.0.0
```

## 🔧 Configuração do Sistema

O arquivo `config.py` centraliza todas as configurações do sistema. Principais opções:

### 📊 **Dados da Empresa**
```python
PERIODO_APURACAO = "03/2025"              # Período MM/AAAA
CNPJ_EMPRESA = "19.310.796/0001-07"       # CNPJ da empresa
CNPJ_OPERADORA_PADRAO = "23.802.218/0001-65"  # CNPJ padrão operadora
```

### 📁 **Arquivos e Dados**
```python
ARQUIVO_EXCEL = 'dados.xlsx'       # Arquivo Excel
PLANILHA = 'MAR 2025'             # Nome da aba
BANCO_DADOS = 'checkpoint_efd.db'  # Banco de checkpoints
```

### ⏱️ **Tempos de Espera**
```python
TEMPO_ESPERA_ASSINADOR = 15        # Aguardar assinatura (segundos)
TIMEOUT_WEBDRIVER = 10             # Timeout operações web
TIMEOUT_ALERTA_SUCESSO = 60        # Detectar sucesso assinatura
TIMEOUT_PROXIMO_CPF = 15           # Timeout próximo CPF
```

### 🖱️ **Configurações de Assinatura**
```python
METODO_ASSINATURA_PADRAO = 1       # 1=Teclado, 2=Mouse
VERIFICACAO_MANUAL_PADRAO = True   # Verificar dados manualmente
```

> 💡 **Importante**: O sistema usa automaticamente essas configurações - não há mais prompts durante a execução!

## 🎛️ Execução Automática

### ✅ **Zero Interação Durante Execução**
O sistema foi atualizado para **não fazer perguntas** durante a execução! Todas as configurações são definidas previamente no `config.py`:

- ✅ **Verificação Manual** → `VERIFICACAO_MANUAL_PADRAO`
- ✅ **Método de Assinatura** → `METODO_ASSINATURA_PADRAO`
- ✅ **Tempos de Espera** → Pré-configurados
- ✅ **Dados da Empresa** → Definidos uma vez

### 🔧 **Personalização Rápida**
```python
# Em config.py - Exemplos de personalização
VERIFICACAO_MANUAL_PADRAO = False    # Modo totalmente automático
METODO_ASSINATURA_PADRAO = 2         # Usar Método B (mouse)
TEMPO_ESPERA_ASSINADOR = 20          # 20 segundos para assinatura
PERIODO_APURACAO = "04/2025"         # Mudança de período
```

### 📝 **Variáveis Disponíveis no config.py**

**🗂️ Configurações Gerais:**
- `URL_BASE` - URL do sistema EFD-REINF
- `ARQUIVO_EXCEL` - Nome do arquivo Excel
- `PLANILHA` - Nome da aba/planilha
- `BANCO_DADOS` - Arquivo do banco de checkpoints

**🏢 Dados da Empresa:**
- `PERIODO_APURACAO` - Período MM/AAAA
- `CNPJ_EMPRESA` - CNPJ da empresa
- `CNPJ_OPERADORA_PADRAO` - CNPJ padrão da operadora

**⏱️ Tempos e Timeouts:**
- `TEMPO_ESPERA_ASSINADOR` - Aguardar aplicativo assinatura
- `TIMEOUT_WEBDRIVER` - Timeout operações web
- `TIMEOUT_ALERTA_SUCESSO` - Detectar sucesso assinatura
- `TIMEOUT_PROXIMO_CPF` - Timeout próximo CPF
- `TEMPO_ESPERA_CLIQUE` - Tempo entre cliques
- `INTERVALO_DIGITACAO_MIN/MAX` - Velocidade digitação
- `INTERVALO_ESPERA_MIN/MAX` - Delays aleatórios

**🌐 Chrome:**
- `CHROME_PROFILE_DIR` - Diretório do perfil
- `CHROME_ARGS` - Argumentos do navegador

**🖱️ PyAutoGUI:**
- `PYAUTOGUI_FAILSAFE` - Ativar/desativar failsafe
- `PYAUTOGUI_PAUSE` - Pausa entre ações
- `ASSINATURA_METODO_A/B_INTERVALO` - Intervalos métodos assinatura

**⚙️ Comportamento:**
- `VERIFICACAO_MANUAL_PADRAO` - Modo manual/automático
- `METODO_ASSINATURA_PADRAO` - Método 1 (teclado) ou 2 (mouse)
- `COORDENADAS_MOUSE_METODO_B` - Coordenadas (x,y) para Método B

> ✅ **Todas essas variáveis são realmente utilizadas pelo sistema!**

### 🖱️ **Coordenadas do Mouse (Método B)**

Quando você configura coordenadas para o Método B, elas são **automaticamente salvas** no `config.py`:

```python
# Exemplo no config.py após configuração
COORDENADAS_MOUSE_METODO_B = (850, 450)  # x=850, y=450
```

**✨ Vantagens:**
- ✅ **Persistente** - Coordenadas salvas entre execuções
- ✅ **Reutilizável** - Opção "3️⃣ Usar coordenadas salvas" funciona
- ✅ **Editável** - Pode alterar manualmente no config.py
- ✅ **Automático** - Salva automaticamente quando configurado

### 📋 **Exemplo de Uso - Método B:**

```bash
# 1. Execute o programa com METODO_ASSINATURA_PADRAO = 2 no config.py
python automacao_efd.py

# 2. Sistema detecta que precisa configurar coordenadas:
🎯 CONFIGURAÇÃO DE COORDENADAS - MÉTODO B
==================================================
Para o Método B, você precisa definir onde clicar na tela.
Opções disponíveis:
1️⃣ - Detectar posição atual do mouse
2️⃣ - Inserir coordenadas manualmente 
3️⃣ - Usar coordenadas salvas anteriormente

# 3. Escolha opção 1, posicione mouse, pressione ENTER
# 4. Sistema salva automaticamente no config.py
# 5. Próximas execuções: opção 3 funcionará perfeitamente!
```

## ⚙️ Configuração Avançada

### 📋 Formato do Excel:
- **Planilha**: `MAR 2025`
- **Colunas obrigatórias**:
  - `TITULAR` - Nome do titular
  - `CPF` - CPF do titular
  - `RELACAO` - Relação do dependente
  - `PLANO` - Nome do plano de saúde
  - `VALOR` - Valor pago

### 🎯 Mapeamento de Dependências:
- `TITULAR` → Não é dependente
- `ESPOSA/ESPOSO` → Cônjuge (1)
- `COMPANHEIRO(A)` → Companheiro(a) (2)
- `FILHA/FILHO` → Filho(a) (3)
- `MÃE/PAI` → Pais (9)
- `AGREGADO` → Outros (99)

## 🔐 Métodos de Assinatura

### Método A - Teclas (Recomendado)
```
⌨️ Sequência: ↑ ↑ Enter
```
- Funciona na maioria dos sistemas
- Não requer configuração de coordenadas
- Mais estável

### Método B - Mouse + Enter
```
🖱️ Sequência: Click(x,y) + Enter
```
- Para sistemas específicos
- Requer configuração de coordenadas
- Permite posicionamento preciso

## 📊 Velocidade e Performance

- **⚡ Processamento**: ~1.5 min/grupo
- **💾 Memória**: ~200MB RAM
- **🌐 Chrome**: Perfil dedicado otimizado
- **📱 Compatibilidade**: Windows 10/11, Linux, macOS

## 🛡️ Segurança

- **🔒 FAILSAFE**: Move mouse para canto = cancela tudo
- **👤 Login manual**: Certificado digital sempre manual
- **💾 Dados locais**: Tudo salvo localmente
- **🌐 Perfil isolado**: Chrome dedicado para automação

## ❓ Solução de Problemas

### Problema: Chrome não abre
```bash
# Verificar se Chrome está instalado
# Executar como administrador se necessário
```

### Problema: Erro de assinatura
```bash
# Verificar se Assinador Serpro está rodando
# Tentar trocar método de assinatura (A ↔ B)
# Verificar coordenadas (Método B)
```

### Problema: CPF não encontrado
```bash
# Verificar formato da planilha Excel
# Confirmar nome da aba (MAR 2025)
# Verificar se CPF está na coluna correta
```

### Problema: Certificado não funciona
```bash
# Fazer login manual primeiro
# Verificar validade do certificado
# Tentar em navegador normal antes
```

## 📈 Relatórios Gerados

### 📊 Planilha de Visualização:
- `visualizacao_checkpoint_YYYYMMDD_HHMMSS.xlsx`
- **Resumo de CPFs**: Status, etapas, dependentes
- **Progresso Detalhado**: Histórico completo
- **Estatísticas**: Totais e percentuais
- **Dependentes**: Detalhes por dependente

### 📋 Relatório de Checkpoint:
- `relatorio_checkpoint_YYYYMMDD_HHMMSS.xlsx`
- **Dados completos** do banco de dados
- **Histórico de progresso** detalhado
- **Status de cada CPF** processado

## 🎉 Casos de Uso

### 👤 Contador/Escritório:
- Processar centenas de CPFs automaticamente
- Relatórios para clientes
- Checkpoints para pausar/retomar

### 🏢 Empresa:
- Declarações de funcionários
- Processamento em lote
- Auditoria completa

### 👨‍💼 Profissional Liberal:
- Clientes diversos
- Economia de tempo
- Processo confiável

## 🔄 Atualizações

O sistema é modular e permite:
- ✅ Novos métodos de assinatura
- ✅ Diferentes formatos de Excel
- ✅ Outros tipos de formulário
- ✅ Integração com APIs

## 📞 Suporte

Para problemas técnicos:
1. **📋 Verificar logs** no terminal
2. **💾 Consultar checkpoints** no gerenciador
3. **📊 Analisar relatórios** gerados
4. **🔄 Resetar progresso** se necessário

## ⚡ Início Rápido

```bash
# 1. Clone/baixe o projeto
# 2. Execute
.\executar.bat

# 3. Configure quando perguntado:
#    - Verificação: S ou N
#    - Método: 1 ou 2
#    - Coordenadas: se método 2

# 4. Faça login no site manualmente
# 5. Aguarde processamento automático!
```

---

**🎯 Sistema completo e pronto para produção!**
**⚡ 100% automático com assinatura eletrônica!**
**📊 Relatórios detalhados e checkpoints inteligentes!**

**Desenvolvido para máxima eficiência e confiabilidade em automação fiscal.** 🚀✨