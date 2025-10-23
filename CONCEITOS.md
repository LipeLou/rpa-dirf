# 📚 Conceitos e Tecnologias Utilizadas

Este documento explica os principais conceitos e tecnologias usadas neste projeto.

## 🎯 Visão Geral

```
┌─────────────┐      HTTP Request       ┌──────────────┐      SQL       ┌──────────┐
│  Navegador  │ ───────────────────────> │ Flask Server │ ──────────────> │ SQLite   │
│  (Chrome)   │ <─────────────────────── │  (Python)    │ <────────────── │   DB     │
└─────────────┘      HTTP Response       └──────────────┘      Data       └──────────┘
      ↑                                                                          ↓
      │                                                                          │
      │                                                                    [devs.db]
      │                                                                          
┌─────────────┐                                                                  
│  Selenium   │ ─ Controla ─> Navegador                                         
│   (Testes)  │                                                                  
└─────────────┘                                                                  
```

## 🌐 Flask - Framework Web

### O que é?
Flask é um micro-framework web em Python usado para criar aplicações web rapidamente.

### Neste projeto:
- **app.py** - Servidor web que roda localmente
- **Rotas** - URLs que respondem a requisições:
  - `/` - Página do formulário
  - `/submit` - Processa dados do formulário
  - `/sucesso` - Página de confirmação
  - `/visualizar` - Exibe dados do banco

### Conceitos principais:
```python
@app.route('/')  # Decorador que define uma rota
def index():     # Função executada quando a rota é acessada
    return render_template('index.html')  # Renderiza template HTML
```

## 🗄️ SQLite - Banco de Dados

### O que é?
SQLite é um banco de dados leve que armazena tudo em um único arquivo.

### Estrutura da Tabela:
```sql
cadastros
├── id (INTEGER) - Identificador único
├── nome (TEXT)
├── sobrenome (TEXT)
├── email (TEXT)
├── lado_dev (TEXT)
├── senioridade (TEXT)
├── tecnologias (TEXT)
├── experiencia (TEXT)
└── data_cadastro (TIMESTAMP)
```

### Operações CRUD:
- **Create**: INSERT INTO cadastros VALUES (...)
- **Read**: SELECT * FROM cadastros
- **Update**: UPDATE cadastros SET ... WHERE id = ?
- **Delete**: DELETE FROM cadastros WHERE id = ?

## 🤖 Selenium - Automação de Testes

### O que é?
Selenium é uma ferramenta que controla navegadores de forma automatizada, simulando ações de um usuário real.

### Componentes:

#### 1. WebDriver
Interface que controla o navegador:
```python
driver = webdriver.Chrome()  # Inicia o Chrome
driver.get("http://localhost:5000")  # Navega para URL
```

#### 2. Localizadores (By)
Formas de encontrar elementos na página:
```python
By.ID              # Por ID: <input id="nome">
By.NAME            # Por name: <input name="email">
By.CLASS_NAME      # Por classe: <div class="campo">
By.CSS_SELECTOR    # Por CSS: input[type="text"]
By.XPATH           # Por XPath: //input[@id="nome"]
By.TAG_NAME        # Por tag: <button>
By.LINK_TEXT       # Por texto do link: <a>Clique aqui</a>
```

#### 3. Ações Comuns
```python
# Encontrar elemento
elemento = driver.find_element(By.ID, "nome")

# Digitar texto
elemento.send_keys("João")

# Clicar
elemento.click()

# Limpar campo
elemento.clear()

# Obter texto
texto = elemento.text

# Verificar se está selecionado
if elemento.is_selected():
    print("Checkbox marcado")

# Verificar se está visível
if elemento.is_displayed():
    print("Elemento visível")
```

#### 4. Select (Dropdowns)
```python
from selenium.webdriver.support.ui import Select

select = Select(driver.find_element(By.ID, "senioridade"))
select.select_by_visible_text("Pleno")    # Por texto visível
select.select_by_value("pleno")           # Por value
select.select_by_index(1)                 # Por índice
```

#### 5. Waits (Esperas)
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Espera explícita - aguarda até 10 segundos
wait = WebDriverWait(driver, 10)
elemento = wait.until(
    EC.presence_of_element_located((By.ID, "nome"))
)

# Espera implícita - aplica para todas as buscas
driver.implicitly_wait(10)
```

## 🎨 HTML + CSS - Interface do Usuário

### Elementos do Formulário:

#### Input Text
```html
<input type="text" name="nome" id="nome" required>
```
- `type="text"` - Campo de texto
- `name` - Nome enviado no POST
- `id` - Identificador único
- `required` - Validação HTML5

#### Input Radio
```html
<input type="radio" name="devweb" value="frontend">
```
- Permite selecionar apenas uma opção
- Mesmo `name` agrupa as opções

#### Input Checkbox
```html
<input type="checkbox" name="tecnologia1" value="HTML">
```
- Permite múltiplas seleções
- Cada checkbox tem `name` único

#### Select (Dropdown)
```html
<select name="senioridade" id="senioridade">
    <option value="junior">Junior</option>
    <option value="pleno">Pleno</option>
    <option value="senior">Senior</option>
</select>
```

#### Textarea
```html
<textarea name="experiencia" id="experiencia"></textarea>
```
- Campo de texto multilinha

## 🔄 Fluxo de Dados

### 1. Usuário preenche formulário
```
Navegador → Campos HTML
```

### 2. Formulário é submetido
```
Form (method="POST", action="/submit")
↓
Flask recebe: request.form.get('nome')
```

### 3. Dados são salvos
```python
conn = sqlite3.connect('devs.db')
cursor.execute('INSERT INTO cadastros VALUES (...)')
conn.commit()
```

### 4. Usuário é redirecionado
```python
return redirect(url_for('sucesso'))
```

### 5. Dados são visualizados
```python
cursor.execute('SELECT * FROM cadastros')
cadastros = cursor.fetchall()
return render_template('visualizar.html', cadastros=cadastros)
```

## 🧪 Padrões de Teste

### 1. Teste de Fluxo Feliz (Happy Path)
Testa o caminho normal esperado:
```python
def test_cadastro_completo():
    # 1. Abrir página
    # 2. Preencher todos os campos
    # 3. Submeter
    # 4. Verificar sucesso
```

### 2. Teste de Validação
Testa casos de erro:
```python
def test_validacao():
    # 1. Tentar submeter vazio
    # 2. Tentar email inválido
    # 3. Verificar mensagens de erro
```

### 3. Teste de Performance
Mede tempo de execução:
```python
def test_performance():
    inicio = time.time()
    # ... realizar ações ...
    tempo_total = time.time() - inicio
```

### 4. Teste de Regressão
Garante que mudanças não quebram funcionalidades existentes.

## 🎯 Boas Práticas Implementadas

### 1. Page Object Model (Conceito)
Encapsular elementos e ações em uma classe:
```python
class FormularioTester:
    def preencher_nome(self, nome):
        # Lógica encapsulada
```

### 2. Waits Explícitos
Melhor que `time.sleep()`:
```python
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "nome"))
)
```

### 3. Try/Finally
Garantir que o navegador fecha:
```python
try:
    # testes
finally:
    driver.quit()
```

### 4. Screenshots em Erros
Capturar evidências:
```python
except Exception as e:
    driver.save_screenshot("erro.png")
```

## 🔍 Seletores CSS Úteis

```css
/* Por ID */
#nome

/* Por classe */
.campo

/* Por atributo */
input[type="text"]
input[name="email"]

/* Descendentes */
form .campo input

/* Pseudo-classes */
input:checked    /* Checkbox/radio marcado */
option:selected  /* Opção selecionada */

/* Múltiplos seletores */
input, select, textarea
```

## 📊 Debugging

### 1. Ver elementos encontrados
```python
elementos = driver.find_elements(By.TAG_NAME, "input")
for el in elementos:
    print(f"Tag: {el.tag_name}, Type: {el.get_attribute('type')}")
```

### 2. Ver HTML da página
```python
print(driver.page_source)
```

### 3. Executar JavaScript
```python
driver.execute_script("alert('Debug!');")
```

### 4. Tirar screenshot
```python
driver.save_screenshot("debug.png")
```

## 🚀 Próximos Passos

Sugestões para expandir seus conhecimentos:

1. **Adicionar mais validações** no formulário
2. **Implementar Page Object Model** completo
3. **Adicionar testes de API** com requests
4. **Usar pytest** para estruturar testes
5. **Configurar CI/CD** com GitHub Actions
6. **Adicionar relatórios** com pytest-html
7. **Testar em múltiplos navegadores** (Firefox, Edge)
8. **Implementar testes paralelos** com pytest-xdist

## 📖 Recursos para Aprender Mais

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [CSS Selectors Reference](https://www.w3schools.com/cssref/css_selectors.asp)
- [XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp)

---

**Bons estudos e bons testes! 🎓**

