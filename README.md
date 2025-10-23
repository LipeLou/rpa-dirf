# 🧪 Projeto de Teste Selenium - Formulário de Cadastro de DEVs

Este projeto foi criado para testar automação com Selenium Python em um formulário web completo com banco de dados.

## 📋 O que tem neste projeto?

- ✅ Formulário HTML completo e estilizado
- ✅ Servidor Flask para rodar o formulário em URL local
- ✅ Banco de dados SQLite para armazenar os cadastros
- ✅ Página de visualização dos dados cadastrados
- ✅ Scripts de teste automatizados com Selenium
- ✅ Interface moderna e responsiva

## 🚀 Como usar?

### 1. Instalar as dependências

Primeiro, certifique-se de ter Python 3 instalado. Depois, instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Instalar o ChromeDriver

O Selenium precisa do ChromeDriver para controlar o navegador Chrome:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver
```

**Ou baixe manualmente:**
- Acesse: https://chromedriver.chromium.org/downloads
- Baixe a versão compatível com seu Chrome
- Extraia e adicione ao PATH do sistema

### 3. Iniciar o servidor Flask

Em um terminal, execute:

```bash
python app.py
```

O servidor estará disponível em:
- **Formulário:** http://localhost:5000
- **Visualizar dados:** http://localhost:5000/visualizar

### 4. Executar os testes Selenium

Com o servidor rodando, **abra outro terminal** e execute:

```bash
python test_selenium.py
```

Escolha qual teste deseja executar:
1. Teste completo do formulário
2. Teste de validação de campos
3. Teste de múltiplos cadastros
4. Executar todos os testes

## 📁 Estrutura do Projeto

```
form/
├── app.py                    # Servidor Flask com rotas e banco de dados
├── test_selenium.py          # Scripts de teste automatizados
├── requirements.txt          # Dependências do projeto
├── devs.db                   # Banco de dados SQLite (criado automaticamente)
├── README.md                 # Este arquivo
└── templates/
    ├── index.html            # Formulário principal
    ├── sucesso.html          # Página de sucesso após cadastro
    └── visualizar.html       # Página para ver todos os cadastros
```

## 🧪 Testes Disponíveis

### 1. Teste Completo do Formulário
- Preenche todos os campos do formulário
- Seleciona opções de radio, select e checkbox
- Submete o formulário
- Verifica redirecionamento para página de sucesso
- Navega para página de visualização

### 2. Teste de Validação
- Tenta submeter o formulário vazio
- Verifica se a validação HTML5 está funcionando

### 3. Teste de Múltiplos Cadastros
- Cadastra vários desenvolvedores em sequência
- Verifica se todos foram salvos corretamente

## 💾 Banco de Dados

O projeto usa SQLite com a seguinte estrutura:

**Tabela: cadastros**
- id (INTEGER, PRIMARY KEY)
- nome (TEXT)
- sobrenome (TEXT)
- email (TEXT)
- lado_dev (TEXT) - frontend, backend ou fullstack
- senioridade (TEXT) - Junior, Pleno ou Senior
- tecnologias (TEXT) - Lista de tecnologias separadas por vírgula
- experiencia (TEXT) - Descrição da experiência
- data_cadastro (TIMESTAMP) - Data e hora do cadastro

## 🎯 Como Criar Seus Próprios Testes

Exemplo básico de teste Selenium:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

# Inicializar driver
driver = webdriver.Chrome()

# Acessar página
driver.get("http://localhost:5000")

# Encontrar e preencher campo
nome = driver.find_element(By.ID, "nome")
nome.send_keys("Seu Nome")

# Clicar em botão
botao = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
botao.click()

# Fechar navegador
driver.quit()
```

## 🔍 Seletores Úteis

### Por ID
```python
driver.find_element(By.ID, "nome")
driver.find_element(By.ID, "email")
driver.find_element(By.ID, "senioridade")
```

### Por CSS Selector
```python
driver.find_element(By.CSS_SELECTOR, "input[value='backend']")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
```

### Por XPath
```python
driver.find_element(By.XPATH, "//input[@name='nome']")
```

## 🛠️ Dicas de Uso

1. **Sempre inicie o servidor Flask antes de executar os testes**
2. **Use time.sleep() com moderação** - prefira WebDriverWait
3. **Feche o navegador após os testes** - use try/finally
4. **Verifique se a porta 5000 está livre** antes de iniciar o servidor
5. **O banco de dados é criado automaticamente** na primeira execução

## 🐛 Solução de Problemas

### Erro: "chromedriver not found"
- Instale o ChromeDriver conforme instruções acima
- Certifique-se de que está no PATH do sistema

### Erro: "Address already in use"
- A porta 5000 já está em uso
- Pare o processo ou mude a porta em app.py

### Navegador não abre
- Verifique se o Chrome está instalado
- Verifique se a versão do ChromeDriver é compatível

### Teste falha ao encontrar elemento
- Verifique se o servidor está rodando
- Adicione WebDriverWait para aguardar carregamento
- Verifique se o seletor está correto

## 📚 Recursos Adicionais

- [Documentação Selenium](https://selenium-python.readthedocs.io/)
- [Documentação Flask](https://flask.palletsprojects.com/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)

## ✨ Melhorias Futuras

- [ ] Adicionar mais campos ao formulário
- [ ] Implementar edição e exclusão de cadastros
- [ ] Adicionar autenticação de usuários
- [ ] Criar testes unitários
- [ ] Adicionar exportação de dados (CSV, Excel)
- [ ] Implementar paginação na visualização

---

**Divirta-se testando com Selenium! 🚀**

