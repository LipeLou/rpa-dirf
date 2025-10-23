# 🚀 INÍCIO RÁPIDO

## ⚡ Setup Automático (Recomendado)

```bash
./setup.sh
```

## 🔧 Setup Manual

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Instalar ChromeDriver (Ubuntu/Debian)
```bash
sudo apt-get install chromium-chromedriver
```

## 🎮 Como Usar

### Terminal 1: Iniciar o Servidor
```bash
python app.py
```

### Terminal 2: Executar Testes
```bash
python test_selenium.py
```

## 🌐 URLs Disponíveis

- **Formulário:** http://localhost:5000
- **Ver Cadastros:** http://localhost:5000/visualizar
- **Página de Sucesso:** http://localhost:5000/sucesso

## 📊 Verificar Banco de Dados

```bash
sqlite3 devs.db "SELECT * FROM cadastros;"
```

## 🧪 Exemplo de Teste Manual

1. Acesse http://localhost:5000
2. Preencha o formulário
3. Clique em "Concluir"
4. Acesse http://localhost:5000/visualizar
5. Veja seus dados salvos!

## 🔥 Dicas Rápidas

- Use **Ctrl+C** para parar o servidor
- O banco de dados é criado automaticamente
- Os testes abrem o navegador automaticamente
- Você pode executar múltiplos testes seguidos

## 🆘 Problemas Comuns

**Porta 5000 em uso?**
```bash
# Encontrar processo
sudo lsof -i :5000

# Matar processo
sudo kill -9 <PID>
```

**ChromeDriver não encontrado?**
```bash
# Verificar instalação
which chromedriver

# Se não encontrado, instale:
sudo apt-get install chromium-chromedriver
```

---
**Tudo pronto! Boa sorte com os testes! 🎉**

