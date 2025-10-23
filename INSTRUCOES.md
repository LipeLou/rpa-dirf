# 📖 Instruções de Uso

## ⚡ Execução Rápida

```bash
python main.py
```

## 🎯 Como Funciona

1. **Chrome abre** no site da Receita Federal
2. **Você faz login** com certificado digital
3. **Sistema mostra** dados de cada grupo (titular + dependentes)
4. **Sistema preenche** automaticamente: Data, CNPJ, CPFs, Relações
5. **Você adiciona** valores e planos de saúde
6. **Você revisa** tudo cuidadosamente
7. **Você envia** manualmente (controle total!)

## 📊 Dados

- **Arquivo:** `dados.xlsx` (aba "MAR 2025")
- **Total:** 451 grupos (titulares)
- **Progresso:** Sistema mostra X/451 em tempo real

## ⌨️ Comandos

Durante execução:
- `S` = Sim, processar este grupo
- `N` = Não, pular
- `P` = Pausar
- `D` = Ver detalhes completos
- `CTRL+C` = Sair

## ⏱️ Tempo

- **Por grupo:** ~1.5 minutos
- **Total (451):** ~11 horas
- **Dica:** Divida em sessões de 2-3h (100 grupos/sessão)

## 🔧 Primeira Instalação

```bash
# Criar ambiente virtual
py -m venv venv

# Ativar
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

## 💡 Dicas

- Login fica salvo após primeira execução
- Pode pausar e continuar depois
- Chrome fica em perfil dedicado (`chrome_assistente/`)
- Se der erro, preencha manualmente e continue

---

Pronto para começar suas instruções! 🚀

