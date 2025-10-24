import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from time import sleep
import pandas as pd
import sqlite3
import os
import urllib.request
import socket

# Configurações fixas
url_base = 'http://localhost:5000'
data = '03/2025'
cnpj = '19.310.796/0001-07'
operadora = '23.802.218/0001-65'

# Arquivo de checkpoint
CHECKPOINT_FILE = 'checkpoint_processamento.txt'

# Ler dados do Excel
dados = pd.read_excel('dados.xlsx', sheet_name='MAR 2025', skiprows=1)

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

def limpar_dataframe(df):
    """
    Limpa o dataframe removendo linhas com valores nulos nas colunas essenciais
    """
    print("🧹 Limpando dataframe...")
    linhas_iniciais = len(df)
    
    # Remover linhas com valores nulos nas colunas essenciais
    df_limpo = df.dropna(subset=['NOME', 'CPF', 'DEPENDENCIA'])
    
    # Remover linhas onde as colunas essenciais são strings vazias ou 'nan'
    df_limpo = df_limpo[
        (df_limpo['NOME'].astype(str).str.strip() != '') &
        (df_limpo['NOME'].astype(str).str.strip().str.lower() != 'nan') &
        (df_limpo['CPF'].astype(str).str.strip() != '') &
        (df_limpo['CPF'].astype(str).str.strip().str.lower() != 'nan') &
        (df_limpo['DEPENDENCIA'].astype(str).str.strip() != '') &
        (df_limpo['DEPENDENCIA'].astype(str).str.strip().str.lower() != 'nan')
    ]
    
    linhas_finais = len(df_limpo)
    print(f"✅ Dataframe limpo: {linhas_iniciais} → {linhas_finais} linhas ({linhas_iniciais - linhas_finais} removidas)")
    
    return df_limpo

# Mapeamento de dependências do dataframe para as opções do select
MAPEAMENTO_DEPENDENCIAS = {
    'TITULAR': 'Titular',
    'ESPOSA': 'Cônjuge',
    'ESPOSO': 'Cônjuge', 
    'COMPANHEIRO(A)': 'Companheiro(a) com o(a) qual tenha filho ou viva há mais de 5 (cinco) anos ou possua declaração de união estável',
    'COMPANHEIRO': 'Companheiro(a) com o(a) qual tenha filho ou viva há mais de 5 (cinco) anos ou possua declaração de união estável',
    'COMPANHEIRA': 'Companheiro(a) com o(a) qual tenha filho ou viva há mais de 5 (cinco) anos ou possua declaração de união estável',
    'FILHA': 'Filho(a) ou enteado(a)',
    'FILHO': 'Filho(a) ou enteado(a)',
    'MAE': 'Pais, avós e bisavós',
    'MÃE': 'Pais, avós e bisavós',
    'MAMAE': 'Pais, avós e bisavós',
    'MAMÃE': 'Pais, avós e bisavós',
    'AGREGADO': 'Agregado/Outros',
    'OUTRA DEPENDENCIA': 'Agregado/Outros',
    'OUTRA DEPENDÊNCIA': 'Agregado/Outros',
    'PAI': 'Pais, avós e bisavós',
    'SOGRO': 'Agregado/Outros',
    'SOGRA': 'Agregado/Outros'
}

def mapear_dependencia(dependencia_dataframe):
    """
    Mapeia a dependência do dataframe para a opção correta do select
    """
    dependencia_upper = str(dependencia_dataframe).strip().upper()
    
    # Buscar mapeamento exato
    if dependencia_upper in MAPEAMENTO_DEPENDENCIAS:
        return MAPEAMENTO_DEPENDENCIAS[dependencia_upper]
    
    # Buscar mapeamento parcial (para variações)
    for key, value in MAPEAMENTO_DEPENDENCIAS.items():
        if key in dependencia_upper or dependencia_upper in key:
            return value
    
    # Se não encontrar, usar "Agregado/Outros" como padrão
    print(f"⚠️ Dependência não mapeada: '{dependencia_dataframe}' - usando 'Agregado/Outros'")
    return 'Agregado/Outros'

def verificar_dados_no_banco(cpf_titular):
    """
    Verifica se os dados foram salvos no banco de dados
    """
    try:
        conn = sqlite3.connect('devs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM efd_declaracoes WHERE cpf = ? ORDER BY id DESC LIMIT 1', (cpf_titular,))
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            print(f"✅ Dados confirmados no banco para CPF: {cpf_titular}")
            print(f"   ID: {resultado[0]}, Data: {resultado[1]}, CNPJ: {resultado[2]}")
            return True
        else:
            print(f"❌ Dados NÃO encontrados no banco para CPF: {cpf_titular}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {str(e)}")
        return False

def salvar_checkpoint(indice_grupo):
    """
    Salva o checkpoint do último grupo processado
    """
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            f.write(str(indice_grupo))
        print(f"💾 Checkpoint salvo: grupo {indice_grupo}")
    except Exception as e:
        print(f"⚠️ Erro ao salvar checkpoint: {str(e)}")

def carregar_checkpoint():
    """
    Carrega o checkpoint do último grupo processado
    Retorna -1 se não houver checkpoint
    """
    try:
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'r') as f:
                indice = int(f.read().strip())
            print(f"📂 Checkpoint encontrado: grupo {indice}")
            return indice
        else:
            print("📂 Nenhum checkpoint encontrado")
            return -1
    except Exception as e:
        print(f"⚠️ Erro ao carregar checkpoint: {str(e)}")
        return -1

def limpar_checkpoint():
    """
    Remove o arquivo de checkpoint
    """
    try:
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
            print("🗑️ Checkpoint removido")
    except Exception as e:
        print(f"⚠️ Erro ao remover checkpoint: {str(e)}")

def verificar_servidor_rodando():
    """
    Verifica se o servidor Flask está rodando em localhost:5000
    """
    try:
        # Tentar conectar na porta 5000
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("✅ Servidor Flask está rodando em http://localhost:5000")
            return True
        else:
            print("\n" + "="*70)
            print("❌ ERRO: Servidor Flask NÃO está rodando!")
            print("="*70)
            print("\n📋 SOLUÇÃO: Antes de executar este script, inicie o servidor Flask:")
            print("\n   1. Abra um NOVO terminal")
            print("   2. Navegue até a pasta do projeto:")
            print(f"      cd {os.getcwd()}")
            print("   3. Ative o ambiente virtual:")
            print("      . venv/bin/activate")
            print("   4. Execute o servidor Flask:")
            print("      python app.py")
            print("\n   O servidor deve mostrar: 🚀 Servidor rodando em: http://localhost:5000")
            print("\n   Depois, volte para este terminal e execute este script novamente.")
            print("\n" + "="*70 + "\n")
            return False
    except Exception as e:
        print(f"⚠️ Erro ao verificar servidor: {str(e)}")
        return False

def processar_dataframe(df):
    """
    Processa o dataframe e agrupa os dados por titular
    Retorna uma lista de grupos, onde cada grupo contém um titular e seus dependentes
    """
    grupos = []
    grupo_atual = []
    
    for index, row in df.iterrows():
        # Pular linhas com valores nulos na coluna NOME
        if pd.isna(row['NOME']) or str(row['NOME']).strip() == '' or str(row['NOME']).strip().lower() == 'nan':
            continue
            
        # Pular linhas com valores nulos na coluna DEPENDENCIA
        if pd.isna(row['DEPENDENCIA']) or str(row['DEPENDENCIA']).strip() == '' or str(row['DEPENDENCIA']).strip().lower() == 'nan':
            continue
            
        # Pular linhas com valores nulos na coluna CPF
        if pd.isna(row['CPF']) or str(row['CPF']).strip() == '' or str(row['CPF']).strip().lower() == 'nan':
            continue
        
        dependencia = str(row['DEPENDENCIA']).strip().upper()
        
        # Se for TITULAR, finaliza o grupo anterior e inicia um novo
        if dependencia == 'TITULAR':
            if grupo_atual:  # Se há um grupo anterior, adiciona à lista
                grupos.append(grupo_atual)
            grupo_atual = [row]  # Inicia novo grupo com o titular
        else:
            # Se não for titular, adiciona como dependente ao grupo atual
            if grupo_atual:  # Só adiciona se há um grupo ativo
                grupo_atual.append(row)
    
    # Adiciona o último grupo se existir
    if grupo_atual:
        grupos.append(grupo_atual)
    
    return grupos

def preparar_dados_teste(grupo):
    """
    Prepara os dados de teste para um grupo (titular + dependentes)
    """
    titular = grupo[0]  # Primeiro item é sempre o titular
    dependentes = grupo[1:] if len(grupo) > 1 else []  # Resto são dependentes
    
    # Dados do titular
    dados_teste = {
        'data': data,
        'cnpj': cnpj,
        'cpf': titular['CPF'],
        'dependentes': [],
        'planos_saude': [],
        'info_dependentes': []
    }
    
    # Adicionar dependentes (filtrar inválidos)
    for dep in dependentes:
        # Verificar se dependente é válido
        if pd.isna(dep['CPF']) or str(dep['CPF']).strip() == '' or str(dep['CPF']).strip().lower() == 'nan':
            print(f"   ⚠️ Pulando dependente inválido - CPF: {dep['CPF']}")
            continue
            
        if pd.isna(dep['DEPENDENCIA']) or str(dep['DEPENDENCIA']).strip() == '' or str(dep['DEPENDENCIA']).strip().lower() == 'nan':
            print(f"   ⚠️ Pulando dependente inválido - DEPENDENCIA: {dep['DEPENDENCIA']}")
            continue
        
        dependencia_original = dep['DEPENDENCIA']
        dependencia_mapeada = mapear_dependencia(dependencia_original)
        
        dependente = {
            'cpf': dep['CPF'],
            'relacao': dependencia_mapeada,
            'agregado_outros': None
        }
        
        # Se for "Agregado/Outros", usar a dependência original como especificação
        if dependencia_mapeada == 'Agregado/Outros':
            dependente['agregado_outros'] = dependencia_original
        
        dados_teste['dependentes'].append(dependente)
        print(f"   📝 Dependente: {dep['CPF']} - {dependencia_original} → {dependencia_mapeada}")
    
    # Adicionar plano de saúde (sempre o mesmo)
    valor_titular = formatar_valor(titular['TOTAL'])
    dados_teste['planos_saude'].append({
        'cnpj': operadora,
        'valor': valor_titular
    })
    
    # Adicionar informações dos dependentes (valores dos dependentes) - filtrar inválidos
    for dep in dependentes:
        # Verificar se dependente é válido
        if pd.isna(dep['CPF']) or str(dep['CPF']).strip() == '' or str(dep['CPF']).strip().lower() == 'nan':
            continue
            
        if pd.isna(dep['TOTAL']) or str(dep['TOTAL']).strip() == '' or str(dep['TOTAL']).strip().lower() == 'nan':
            print(f"   ⚠️ Pulando informação - TOTAL inválido para CPF: {dep['CPF']}")
            continue
        
        valor_dependente = formatar_valor(dep['TOTAL'])
        
        info_dependente = {
            'cpf': dep['CPF'],
            'valor': valor_dependente
        }
        dados_teste['info_dependentes'].append(info_dependente)
    
    return dados_teste

class EFDTestRunner:
    def __init__(self):
        """Inicializa o driver do Chrome"""
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura e cria o driver do Chrome"""
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-data-dir=/tmp/selenium_chrome_profile')
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def close_driver(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def navegar_para_formulario(self):
        """Navega para o formulário EFD-REINF"""
        try:
            self.driver.get(url_base)
            print("✅ Menu principal carregado")
            
            
            formulario_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Acessar Formulário')]")
            formulario_link.click()
            print("✅ Navegando para o formulário EFD-REINF")
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "data"))
            )
            print("✅ Formulário EFD-REINF carregado")
            return True
        except Exception as e:
            print(f"❌ Erro ao navegar para formulário: {str(e)}")
            return False
    
    def preencher_dados_iniciais(self, data=None, cpf=None):
        """Preenche os dados iniciais do formulário"""
        try:
            print("\n📝 Preenchendo dados iniciais...")
                        
            # Data (usar valor fornecido ou manter o padrão)
            if data:
                data_field = self.driver.find_element(By.ID, "data")
                data_field.clear()
                data_field.send_keys(data)
                print(f"✅ Data preenchida: {data}")
            else:
                data_field = self.driver.find_element(By.ID, "data")
                print(f"✅ Data (padrão): {data_field.get_attribute('value')}")
            
            # CNPJ
            cnpj_field = self.driver.find_element(By.ID, "cnpj")
            cnpj_field.clear()
            cnpj_field.send_keys(cnpj)
            print(f"✅ CNPJ preenchido: {cnpj}")
                        
            # CPF
            if cpf:
                cpf_field = self.driver.find_element(By.ID, "cpf")
                cpf_field.clear()
                cpf_field.send_keys(cpf)
                print(f"✅ CPF preenchido: {cpf}")
                        
            return True
        except Exception as e:
            print(f"❌ Erro ao preencher dados iniciais: {str(e)}")
            return False
    
    def continuar_para_proxima_etapa(self):
        """Clica no botão Continuar para ir para a próxima etapa"""
        try:
            continuar_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continuar')]")
            continuar_btn.click()
            print("✅ Clicado em Continuar")
                        
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Incluir Dependente')]"))
            )
            print("✅ Segunda etapa carregada")
            return True
        except Exception as e:
            print(f"❌ Erro ao continuar para próxima etapa: {str(e)}")
            return False
    
    def adicionar_dependente(self, cpf_dependente, relacao, agregado_outros=None):
        """Adiciona um dependente ao formulário"""
        try:
            # Verificar se CPF é válido
            if pd.isna(cpf_dependente) or str(cpf_dependente).strip() == '' or str(cpf_dependente).strip().lower() == 'nan':
                print(f"⚠️ Pulando dependente - CPF inválido: {cpf_dependente}")
                return True  # Retorna True para não interromper o fluxo
            
            print(f"\n👥 Adicionando dependente: {cpf_dependente}")
            
            # Abrir modal
            incluir_dependente_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Incluir Dependente')]")
            incluir_dependente_btn.click()
            print("✅ Modal de dependente aberto")
                        
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "dependenteCpf"))
            )
            
            # Preencher CPF
            dependente_cpf = self.driver.find_element(By.ID, "dependenteCpf")
            dependente_cpf.send_keys(cpf_dependente)
            print(f"✅ CPF do dependente preenchido: {cpf_dependente}")
                        
            # Selecionar relação
            relacao_select = Select(self.driver.find_element(By.ID, "relacaoDependencia"))
            relacao_select.select_by_visible_text(relacao)
            print(f"✅ Relação selecionada: {relacao}")
                        
            # Se for "Agregado/Outros", preencher campo específico
            if relacao == "Agregado/Outros" and agregado_outros:
                # Verificar se agregado_outros é válido
                if not pd.isna(agregado_outros) and str(agregado_outros).strip() != '' and str(agregado_outros).strip().lower() != 'nan':
                    # Aguardar campo aparecer
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.ID, "agregadoOutros"))
                    )
                    agregado_field = self.driver.find_element(By.ID, "agregadoOutros")
                    agregado_field.send_keys(agregado_outros)
                    print(f"✅ Campo agregado preenchido: {agregado_outros}")
            
            # Adicionar
            adicionar_btn = self.driver.find_element(By.XPATH, "//div[@id='modalDependente']//button[contains(text(), 'Adicionar')]")
            adicionar_btn.click()
            print("✅ Dependente adicionado")
                        
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "modalDependente"))
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar dependente: {str(e)}")
            return False
    
    def adicionar_plano_saude(self, operadora, valor):
        """Adiciona um plano de saúde ao formulário"""
        try:
            print(f"\n🏥 Adicionando plano de saúde: {operadora}")
            
            # Abrir modal
            incluir_plano_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Incluir Plano de Saúde')]")
            incluir_plano_btn.click()
            print("✅ Modal de plano de saúde aberto")
                        
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "planoCnpj"))
            )
            
            # Preencher CNPJ
            plano_cnpj = self.driver.find_element(By.ID, "planoCnpj")
            plano_cnpj.send_keys(operadora)
            print(f"✅ CNPJ do plano preenchido: {operadora}")
                        
            # Preencher valor
            valor_pago = self.driver.find_element(By.ID, "valorPago")
            valor_pago.send_keys(valor)
            print(f"✅ Valor preenchido: R$ {valor}")
                        
            # Adicionar
            adicionar_btn = self.driver.find_element(By.XPATH, "//div[@id='modalPlanoSaude']//button[contains(text(), 'Adicionar')]")
            adicionar_btn.click()
            print("✅ Plano de saúde adicionado")
                        
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "modalPlanoSaude"))
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar plano de saúde: {str(e)}")
            return False
    
    def adicionar_informacao_dependente(self, cpf_dependente, valor):
        """Adiciona informação de dependente (valor)"""
        try:
            # Verificar se CPF é válido
            if pd.isna(cpf_dependente) or str(cpf_dependente).strip() == '' or str(cpf_dependente).strip().lower() == 'nan':
                print(f"⚠️ Pulando informação do dependente - CPF inválido: {cpf_dependente}")
                return True  # Retorna True para não interromper o fluxo
            
            print(f"\n💰 Adicionando informação do dependente: {cpf_dependente}")
                        
            # Aguardar botão aparecer
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Adicionar Informações dos Dependentes')]"))
            )
            
            # Abrir modal
            adicionar_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Adicionar Informações dos Dependentes')]")
            adicionar_btn.click()
            print("✅ Modal de informações dos dependentes aberto")
                        
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "dependenteSelecionado"))
            )
            
            # Selecionar dependente pelo CPF
            dependente_select = Select(self.driver.find_element(By.ID, "dependenteSelecionado"))
            dependente_select.select_by_visible_text(cpf_dependente)
            print(f"✅ Dependente selecionado: {cpf_dependente}")
                        
            # Preencher valor
            valor_field = self.driver.find_element(By.ID, "valorDependente")
            valor_field.send_keys(valor)
            print(f"✅ Valor preenchido: R$ {valor}")
                        
            # Adicionar
            adicionar_btn = self.driver.find_element(By.XPATH, "//div[@id='modalDependentePlano']//button[contains(text(), 'Adicionar')]")
            adicionar_btn.click()
            print("✅ Informação do dependente adicionada")
                        
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "modalDependentePlano"))
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar informação do dependente: {str(e)}")
            return False
    
    def enviar_declaracao(self):
        """Envia a declaração"""
        try:
            print("\n🚀 Enviando declaração...")
            
            enviar_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Enviar Declaração')]")
            enviar_btn.click()
            print("✅ Declaração enviada")
                        
            # Aguardar página de sucesso
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/sucesso_efd")
            )
            print("✅ Redirecionado para página de sucesso")
                        
            # Verificar sucesso
            sucesso_title = self.driver.find_element(By.CLASS_NAME, "title")
            assert "Declaração Enviada com Sucesso!" in sucesso_title.text
            print("✅ Página de sucesso carregada corretamente")
            
            # Aguardar mais tempo para garantir que salvou no banco
           # time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar declaração: {str(e)}")
            # Tirar screenshot para debug
            self.tirar_screenshot(f"erro_envio_{int(time.time())}.png")
            return False
    
    def executar_teste_completo(self, dados_teste):
        """Executa um teste completo com os dados fornecidos"""
        try:
            print(f"🔍 Iniciando teste para: {dados_teste.get('cpf', 'N/A')}")
            
            # Navegar para formulário
            if not self.navegar_para_formulario():
                return False
            
            # Preencher dados iniciais
            if not self.preencher_dados_iniciais(
                data=dados_teste.get('data'),
                cpf=dados_teste.get('cpf')
            ):
                return False
            
            # Continuar para próxima etapa
            if not self.continuar_para_proxima_etapa():
                return False
            
            # Adicionar dependentes (se houver)
            dependentes = dados_teste.get('dependentes', [])
            for dep in dependentes:
                if not self.adicionar_dependente(
                    cpf_dependente=dep.get('cpf'),
                    relacao=dep.get('relacao'),
                    agregado_outros=dep.get('agregado_outros')
                ):
                    return False
            
            # Adicionar planos de saúde
            planos = dados_teste.get('planos_saude', [])
            for plano in planos:
                if not self.adicionar_plano_saude(
                    operadora=plano.get('cnpj'),
                    valor=plano.get('valor')
                ):
                    return False
            
            # Adicionar informações dos dependentes (se houver)
            info_dependentes = dados_teste.get('info_dependentes', [])
            for info in info_dependentes:
                if not self.adicionar_informacao_dependente(
                    cpf_dependente=info.get('cpf'),
                    valor=info.get('valor')
                ):
                    return False
            
            # Enviar declaração
            if not self.enviar_declaracao():
                return False
            
            # Verificar se os dados foram salvos no banco
            cpf_titular = dados_teste.get('cpf', 'N/A')
            dados_salvos = verificar_dados_no_banco(cpf_titular)
            
            if dados_salvos:
                print(f"✨ Teste concluído com sucesso para: {cpf_titular}")
                return True
            else:
                print(f"❌ Teste falhou - dados não salvos no banco para: {cpf_titular}")
                return False
            
        except Exception as e:
            print(f"❌ Erro durante teste completo: {str(e)}")
            self.tirar_screenshot(f"erro_teste_{dados_teste.get('cpf', 'unknown')}.png")
            return False
    
    def tirar_screenshot(self, nome_arquivo="erro_efd_test.png"):
        """Tira screenshot em caso de erro"""
        try:
            self.driver.save_screenshot(nome_arquivo)
            print(f"📸 Screenshot salvo como '{nome_arquivo}'")
        except:
            pass


# Função principal para executar testes individuais
def executar_teste_individual(dados_teste):
    """Executa um teste individual com os dados fornecidos"""
    runner = EFDTestRunner()
    try:
        resultado = runner.executar_teste_completo(dados_teste)
        return resultado
    finally:
        runner.close_driver()


def processar_todos_os_grupos(continuar_de_onde_parou=True):
    """
    Processa todos os grupos do dataframe e executa os testes
    
    Args:
        continuar_de_onde_parou: Se True, continua do último checkpoint. Se False, começa do zero.
    """
    # Verificar se o servidor Flask está rodando
    if not verificar_servidor_rodando():
        return None
    
    print("\n🔍 Iniciando processamento do dataframe...")
    print(f"📊 Total de linhas no dataframe: {len(dados_limpos)}")
    
    # Processar dataframe e agrupar por titular
    grupos = processar_dataframe(dados_limpos)
    print(f"👥 Total de grupos (titulares) encontrados: {len(grupos)}")
    
    # Verificar checkpoint
    inicio = 0
    if continuar_de_onde_parou:
        checkpoint = carregar_checkpoint()
        if checkpoint >= 0:
            resposta = input(f"\n🔄 Checkpoint encontrado no grupo {checkpoint}. Deseja continuar de onde parou? (s/n): ")
            if resposta.lower() in ['s', 'sim', 'y', 'yes']:
                inicio = checkpoint + 1
                print(f"▶️ Continuando do grupo {inicio + 1}")
            else:
                limpar_checkpoint()
                print("🔄 Iniciando do zero")
        else:
            print("🔄 Nenhum checkpoint encontrado. Iniciando do zero")
    else:
        limpar_checkpoint()
        print("🔄 Iniciando do zero (checkpoint ignorado)")
    
    # Verificar se já terminou
    if inicio >= len(grupos):
        print("✅ Todos os grupos já foram processados!")
        limpar_checkpoint()
        return None
    
    resultados = []
    
    print(f"\n📊 Processando grupos {inicio + 1} até {len(grupos)}")
    
    try:
        for i in range(inicio, len(grupos)):
            print(f"\n{'='*60}")
            print(f"🔄 Processando grupo {i + 1}/{len(grupos)}")
            
            grupo = grupos[i]
            titular = grupo[0]
            dependentes = grupo[1:] if len(grupo) > 1 else []
            
            print(f"👤 Titular: {titular['NOME']} - CPF: {titular['CPF']}")
            print(f"👥 Dependentes: {len(dependentes)}")
            
            # Preparar dados do teste
            dados_teste = preparar_dados_teste(grupo)
            
            # Executar teste
            try:
                resultado = executar_teste_individual(dados_teste)
                status = 'Sucesso' if resultado else 'Falha'
                print(f"✅ Resultado: {status}")
                
                resultados.append({
                    'grupo': i + 1,
                    'titular_nome': titular['NOME'],
                    'titular_cpf': titular['CPF'],
                    'dependentes_count': len(dependentes),
                    'resultado': status,
                    'timestamp': pd.Timestamp.now()
                })
                
                # Salvar checkpoint após cada grupo processado com sucesso
                salvar_checkpoint(i)
                
            except KeyboardInterrupt:
                print(f"\n\n⏸️ Processamento pausado pelo usuário no grupo {i + 1}")
                print(f"💾 Checkpoint salvo. Execute novamente para continuar de onde parou.")
                salvar_checkpoint(i - 1 if i > 0 else 0)  # Salvar grupo anterior para reprocessar o atual
                
                # Salvar resultados parciais
                if resultados:
                    df_resultados = pd.DataFrame(resultados)
                    df_resultados.to_excel('resultados_processamento_parcial.xlsx', index=False)
                    print(f"📄 Resultados parciais salvos em: resultados_processamento_parcial.xlsx")
                
                raise  # Re-lançar a exceção para sair do programa
                
            except Exception as e:
                print(f"❌ Erro no grupo {i + 1}: {str(e)}")
                resultados.append({
                    'grupo': i + 1,
                    'titular_nome': titular['NOME'],
                    'titular_cpf': titular['CPF'],
                    'dependentes_count': len(dependentes),
                    'resultado': 'Erro',
                    'erro': str(e),
                    'timestamp': pd.Timestamp.now()
                })
                
                # Salvar checkpoint mesmo em caso de erro para pular este grupo
                salvar_checkpoint(i)
        
        # Se chegou aqui, processou tudo com sucesso
        limpar_checkpoint()
        print("\n🎉 Todos os grupos foram processados!")
        
    except KeyboardInterrupt:
        # Se foi interrompido, retornar resultados parciais
        if resultados:
            return pd.DataFrame(resultados)
        return None
    
    # Salvar resultados
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_excel('resultados_processamento.xlsx', index=False)
    
    # Mostrar resumo
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS RESULTADOS")
    print(f"{'='*60}")
    print(f"Total de grupos processados: {len(resultados)}")
    print(f"Sucessos: {len([r for r in resultados if r['resultado'] == 'Sucesso'])}")
    print(f"Falhas: {len([r for r in resultados if r['resultado'] == 'Falha'])}")
    print(f"Erros: {len([r for r in resultados if r['resultado'] == 'Erro'])}")
    print(f"\n📄 Resultados salvos em: resultados_processamento.xlsx")
    
    return df_resultados

def mostrar_estrutura_dataframe():
    """
    Mostra a estrutura do dataframe para debug
    """
    print("📋 ESTRUTURA DO DATAFRAME:")
    print(f"Colunas: {list(dados_limpos.columns)}")
    print(f"Total de linhas: {len(dados_limpos)}")
    print("\nPrimeiras 5 linhas:")
    print(dados_limpos.head())
    print("\nValores únicos em DEPENDENCIA:")
    print(dados_limpos['DEPENDENCIA'].value_counts())
    
    print("\n🔄 MAPEAMENTO DE DEPENDÊNCIAS:")
    dependencias_unicas = dados_limpos['DEPENDENCIA'].unique()
    for dep in dependencias_unicas:
        if pd.notna(dep):
            mapeada = mapear_dependencia(dep)
            print(f"   '{dep}' → '{mapeada}'")

def mostrar_status_banco():
    """
    Mostra o status atual do banco de dados
    """
    try:
        conn = sqlite3.connect('devs.db')
        cursor = conn.cursor()
        
        # Contar total de registros
        cursor.execute('SELECT COUNT(*) FROM efd_declaracoes')
        total = cursor.fetchone()[0]
        
        # Últimos 5 registros
        cursor.execute('SELECT id, cpf, data, data_cadastro FROM efd_declaracoes ORDER BY id DESC LIMIT 5')
        ultimos = cursor.fetchall()
        
        conn.close()
        
        print(f"\n🗄️ STATUS DO BANCO DE DADOS:")
        print(f"Total de declarações: {total}")
        print("\nÚltimos 5 registros:")
        for registro in ultimos:
            print(f"  ID: {registro[0]} | CPF: {registro[1]} | Data: {registro[2]} | Cadastro: {registro[3]}")
            
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {str(e)}")

def testar_grupo_especifico(indice_grupo):
    """
    Testa apenas um grupo específico (útil para debug)
    """
    # Verificar se o servidor Flask está rodando
    if not verificar_servidor_rodando():
        return False
    
    print(f"\n🔍 Testando grupo específico: {indice_grupo}")
    
    # Processar dataframe
    grupos = processar_dataframe(dados_limpos)
    
    if indice_grupo >= len(grupos):
        print(f"❌ Grupo {indice_grupo} não existe. Total de grupos: {len(grupos)}")
        return False
    
    grupo = grupos[indice_grupo]
    titular = grupo[0]
    dependentes = grupo[1:] if len(grupo) > 1 else []
    
    print(f"👤 Titular: {titular['NOME']} - CPF: {titular['CPF']}")
    print(f"👥 Dependentes: {len(dependentes)}")
    
    # Preparar dados
    dados_teste = preparar_dados_teste(grupo)
    
    # Executar teste
    resultado = executar_teste_individual(dados_teste)
    
    print(f"Resultado: {'✅ Sucesso' if resultado else '❌ Falha'}")
    return resultado

def testar_mapeamento_dependencias():
    """
    Testa o mapeamento de dependências sem executar o formulário
    """
    print("🧪 TESTANDO MAPEAMENTO DE DEPENDÊNCIAS")
    print("="*50)
    
    dependencias_unicas = dados_limpos['DEPENDENCIA'].unique()
    
    for dep in dependencias_unicas:
        if pd.notna(dep):
            mapeada = mapear_dependencia(dep)
            print(f"'{dep}' → '{mapeada}'")
    
    print("\n✅ Mapeamento testado com sucesso!")

def mostrar_status_checkpoint():
    """
    Mostra o status atual do checkpoint
    """
    checkpoint = carregar_checkpoint()
    grupos = processar_dataframe(dados_limpos)
    total_grupos = len(grupos)
    
    print(f"\n📊 STATUS DO CHECKPOINT")
    print(f"{'='*60}")
    print(f"Total de grupos: {total_grupos}")
    
    if checkpoint >= 0:
        print(f"Último grupo processado: {checkpoint + 1}")
        print(f"Próximo grupo a processar: {checkpoint + 2}")
        print(f"Grupos restantes: {total_grupos - checkpoint - 1}")
        print(f"Progresso: {((checkpoint + 1) / total_grupos * 100):.1f}%")
    else:
        print("Nenhum grupo processado ainda")
        print(f"Progresso: 0.0%")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # Limpar dataframe
    dados_limpos = limpar_dataframe(dados)
    
    # Mostrar estrutura do dataframe
    mostrar_estrutura_dataframe()
    
    # Testar mapeamento de dependências
    testar_mapeamento_dependencias()
    
    # Mostrar status inicial do banco
    mostrar_status_banco()
    
    # Processar todos os grupos
    processar_todos_os_grupos()
    
    # Mostrar status final do banco
    print(f"\n{'='*60}")
    print("STATUS FINAL DO BANCO DE DADOS")
    mostrar_status_banco()
