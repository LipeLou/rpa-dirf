from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)

def formatar_valor(valor):
    """
    Formata um valor para 2 casas decimais no padrão brasileiro (vírgula)
    """
    try:
        if isinstance(valor, str):
            valor = valor.replace(',', '.')
        valor_float = float(valor)
        return f"{valor_float:.2f}".replace('.', ',')
    except (ValueError, TypeError):
        return '0,00'

# Função para inicializar o banco de dados
def init_db():
    conn = sqlite3.connect('devs.db')
    cursor = conn.cursor()
    
    # Tabela original para desenvolvedores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            email TEXT NOT NULL,
            lado_dev TEXT NOT NULL,
            senioridade TEXT NOT NULL,
            tecnologias TEXT NOT NULL,
            experiencia TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Nova tabela para EFD-REINF
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS efd_declaracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            cnpj TEXT NOT NULL,
            cpf TEXT NOT NULL,
            dependentes TEXT,
            planos_saude TEXT,
            dependentes_planos TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Rota principal - exibe o menu
@app.route('/')
def index():
    return render_template('menu.html')

# Rota para o formulário EFD-REINF
@app.route('/formulario')
def formulario_efd():
    return render_template('formulario_efd.html')

# Rota para processar o formulário
@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form.get('nome')
    sobrenome = request.form.get('sobrenome')
    email = request.form.get('email')
    lado_dev = request.form.get('devweb')
    senioridade = request.form.get('senioridade')
    
    # Pegar todas as tecnologias selecionadas
    tecnologias = []
    for i in range(1, 8):
        tech = request.form.get(f'tecnologia{i}')
        if tech:
            tecnologias.append(tech)
    tecnologias_str = ', '.join(tecnologias) if tecnologias else 'Nenhuma'
    
    experiencia = request.form.get('experiencia', '')
    
    # Salvar no banco de dados
    conn = sqlite3.connect('devs.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cadastros (nome, sobrenome, email, lado_dev, senioridade, tecnologias, experiencia)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nome, sobrenome, email, lado_dev, senioridade, tecnologias_str, experiencia))
    conn.commit()
    conn.close()
    
    return redirect(url_for('sucesso'))

# Rota para processar o formulário EFD-REINF
@app.route('/submit_efd', methods=['POST'])
def submit_efd():
    data = request.form.get('data')
    cnpj = request.form.get('cnpj')
    cpf = request.form.get('cpf')
    
    # Pegar dados dos dependentes, planos e dependentes com planos
    dependentes = request.form.get('dependentes', '[]')
    planos_saude = request.form.get('planos_saude', '[]')
    dependentes_planos = request.form.get('dependentes_planos', '[]')
    
    # Salvar no banco de dados
    conn = sqlite3.connect('devs.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO efd_declaracoes (data, cnpj, cpf, dependentes, planos_saude, dependentes_planos)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data, cnpj, cpf, dependentes, planos_saude, dependentes_planos))
    conn.commit()
    conn.close()
    
    return redirect(url_for('sucesso_efd'))

# Rota de sucesso para EFD-REINF
@app.route('/sucesso_efd')
def sucesso_efd():
    return render_template('sucesso_efd.html')

# Rota de sucesso (original)
@app.route('/sucesso')
def sucesso():
    return render_template('sucesso.html')

# Rota para visualizar todos os cadastros
@app.route('/visualizar')
def visualizar():
    conn = sqlite3.connect('devs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cadastros ORDER BY id DESC')
    cadastros = cursor.fetchall()
    conn.close()
    return render_template('visualizar.html', cadastros=cadastros)

# Rota para visualizar declarações EFD-REINF
@app.route('/visualizar_efd')
def visualizar_efd():
    conn = sqlite3.connect('devs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM efd_declaracoes ORDER BY id DESC')
    declaracoes = cursor.fetchall()
    conn.close()
    return render_template('visualizar_efd.html', declaracoes=declaracoes)

# Rota para obter detalhes de uma declaração EFD-REINF
@app.route('/detalhes_efd/<int:declaracao_id>')
def detalhes_efd(declaracao_id):
    import json
    
    try:
        conn = sqlite3.connect('devs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM efd_declaracoes WHERE id = ?', (declaracao_id,))
        declaracao = cursor.fetchone()
        conn.close()
        
        if not declaracao:
            return jsonify({'error': 'Declaração não encontrada'}), 404
        
        # Estrutura: id, data, cnpj, cpf, dependentes, planos_saude, dependentes_planos, data_cadastro
        dependentes = json.loads(declaracao[4]) if declaracao[4] else []
        planos_saude = json.loads(declaracao[5]) if declaracao[5] else []
        dependentes_planos = json.loads(declaracao[6]) if declaracao[6] else []
        
        # Valor do titular (primeiro plano de saúde)
        valor_titular = formatar_valor(planos_saude[0]['valor']) if planos_saude else '0,00'
        
        # Combinar dependentes com valores
        dependentes_completos = []
        for dep in dependentes:
            valor_dependente = '0,00'
            for dp in dependentes_planos:
                if dp['cpf'] == dep['cpf']:
                    valor_dependente = formatar_valor(dp['valor'])
                    break
            
            dependentes_completos.append({
                'cpf': dep['cpf'],
                'relacao': dep['relacao'],
                'valor': valor_dependente
            })
        
        return jsonify({
            'id': declaracao[0],
            'data': declaracao[1],
            'cnpj': declaracao[2],
            'cpf': declaracao[3],
            'data_cadastro': declaracao[7],
            'valor_titular': valor_titular,
            'dependentes': dependentes_completos
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    print("🚀 Servidor rodando em: http://localhost:5000")
    print("📊 Visualizar dados em: http://localhost:5000/visualizar")
    app.run(debug=True, port=5000)

