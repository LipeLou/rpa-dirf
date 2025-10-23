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

# Configurações fixas
url_base = 'http://www3.cav.receita.fazenda.gov.br/reinfweb/#/home'
data = '03/2025'
cnpj = '19.310.796/0001-07'
operadora = '23.802.218/0001-65'
tempo_espera = 3

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
            
            
            formulario_link = self.driver.find_element(By.XPATH, '//a[@data-testid="menu_incluir_pagamento_credito"]')
            formulario_link.click()
            print("✅ Navegando para o formulário EFD-REINF")
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "periodo_apuracao"))
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

            # Data
            data_field = self.driver.find_element(By.ID, "periodo_apuracao")
            data_field.clear()
            data_field.send_keys(data)
            print(f"✅ Data preenchida: {data}")
            time.sleep(tempo_espera)

            # CNPJ
            cnpj_field = self.driver.find_element(By.ID, "insc_estabelecimento")
            cnpj_field.clear()
            cnpj_field.send_keys(cnpj)
            print(f"✅ CNPJ preenchido: {cnpj}")
            time.sleep(tempo_espera)
                        
            # CPF
            if cpf:
                cpf_field = self.driver.find_element(By.ID, "cpf_beneficiario")
                cpf_field.clear()
                cpf_field.send_keys(cpf)
                print(f"✅ CPF preenchido: {cpf}")
                time.sleep(tempo_espera)
                
            return True
        except Exception as e:
            print(f"❌ Erro ao preencher dados iniciais: {str(e)}")    
            return False
    
    def continuar_para_proxima_etapa(self):
        """Clica no botão Continuar para ir para a próxima etapa"""
        try:
            continuar_btn = self.driver.find_element(By.XPATH, '//a[@data-testid="botao_continuar"]')
            continuar_btn.click()
            print("✅ Clicado em Continuar")
                        
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'BotaoInclusaoDiv_ideDep'))
            )
            print("✅ Segunda etapa carregada")
            time.sleep(tempo_espera)
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
            incluir_dependente_btn = self.driver.find_element(By.ID, 'BotaoInclusaoDiv_ideDep')
            incluir_dependente_btn.click()
            print("✅ Modal de dependente aberto")
            time.sleep(tempo_espera)            
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//input[@data-testid="cpf_dependente"]'))
            )
            
            # Preencher CPF
            dependente_cpf = self.driver.find_element(By.XPATH, '//input[@data-testid="cpf_dependente"]')
            dependente_cpf.send_keys(cpf_dependente)
            print(f"✅ CPF do dependente preenchido: {cpf_dependente}")
            time.sleep(tempo_espera)            
            # Selecionar relação
            relacao_select = Select(self.driver.find_element(By.XPATH, '//select[@data-testid="relacao_dependencia"]'))
            relacao_select.select_by_visible_text(relacao)
            print(f"✅ Relação selecionada: {relacao}")
            time.sleep(tempo_espera)
            # Se for "Agregado/Outros", preencher campo específico
            if relacao == "Agregado/Outros" and agregado_outros:
                # Verificar se agregado_outros é válido
                if not pd.isna(agregado_outros) and str(agregado_outros).strip() != '' and str(agregado_outros).strip().lower() != 'nan':
                    # Aguardar campo aparecer
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@data-testid="descricao_dependencia"]'))
                    )
                    agregado_field = self.driver.find_element(By.XPATH, '//input[@data-testid="descricao_dependencia"]')
                    agregado_field.send_keys(agregado_outros)
                    print(f"✅ Campo agregado preenchido: {agregado_outros}")
            
            # Adicionar
            adicionar_btn = self.driver.find_element(By.XPATH, "//div[@data-testid='botao_salvar_modal_ide_dep']")
            adicionar_btn.click()
            print("✅ Dependente adicionado")
            time.sleep(tempo_espera)            

            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar dependente: {str(e)}")
            return False
    
    def adicionar_plano_saude(self, operadora, valor):
        """Adiciona um plano de saúde ao formulário"""
        try:
            print(f"\n🏥 Adicionando plano de saúde: {operadora}")
            
            # Abrir modal
            incluir_plano_btn = self.driver.find_element(By.ID, 'BotaoInclusaoDiv_ideOpSaude')
            incluir_plano_btn.click()
            print("✅ Modal de plano de saúde aberto")
                        
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//input[@data-testid="cnpj_operadora"]'))
            )
            
            # Preencher CNPJ
            plano_cnpj = self.driver.find_element(By.XPATH, '//input[@data-testid="cnpj_operadora"]')
            plano_cnpj.send_keys(operadora)
            print(f"✅ CNPJ do plano preenchido: {operadora}")
            time.sleep(tempo_espera)
            # Preencher valor
            valor_pago = self.driver.find_element(By.XPATH, '//input[@data-testid="valor_saude"]')
            valor_pago.send_keys(valor)
            print(f"✅ Valor preenchido: R$ {valor}")
            time.sleep(tempo_espera)
            # Adicionar
            adicionar_btn = self.driver.find_element(By.XPATH, "//div[@id='botao_salvar_modal_ide_op_saude']")
            adicionar_btn.click()
            print("✅ Plano de saúde adicionado")
            time.sleep(tempo_espera)

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
                EC.presence_of_element_located((By.ID, 'BotaoInclusaoDiv_infoDependP1_0'))
            )
            
            # Abrir modal
            adicionar_btn = self.driver.find_element(By.ID, 'BotaoInclusaoDiv_infoDependP1_0')
            adicionar_btn.click()
            print("✅ Modal de informações dos dependentes aberto")
            time.sleep(tempo_espera)
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//select[@data-testid="c_p_f_do_dependente"]'))
            )
            
            # Selecionar dependente pelo CPF
            dependente_select = Select(self.driver.find_element(By.XPATH, '//select[@data-testid="c_p_f_do_dependente"]'))
            dependente_select.select_by_visible_text(cpf_dependente)
            print(f"✅ Dependente selecionado: {cpf_dependente}")
            time.sleep(tempo_espera)            
            # Preencher valor
            valor_field = self.driver.find_element(By.XPATH, '//input[@data-testid="valor_saude_plano"]')
            valor_field.send_keys(valor)
            print(f"✅ Valor preenchido: R$ {valor}")
            time.sleep(tempo_espera)
            # Adicionar
            adicionar_btn = self.driver.find_element(By.XPATH, "//div[@data-testid='botao_salvar_modal_info_depend_pl']")
            adicionar_btn.click()
            print("✅ Informação do dependente adicionada")
            time.sleep(tempo_espera)

            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar informação do dependente: {str(e)}")
            return False
    
    def enviar_declaracao(self):
        """Envia a declaração - DESATIVADO PARA TESTES"""
        try:
            print("\n🚀 [DESATIVADO] Enviando declaração...")
            print("⚠️ FUNÇÃO DESATIVADA - Não enviando dados para o site oficial")
            
            # Simular sucesso sem enviar
            print("✅ [SIMULADO] Declaração enviada")
            print("✅ [SIMULADO] Redirecionado para página de sucesso")
            print("✅ [SIMULADO] Página de sucesso carregada corretamente")
            
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
            
            # Verificação do banco desativada para testes no site oficial
            cpf_titular = dados_teste.get('cpf', 'N/A')
            print(f"⚠️ [DESATIVADO] Verificação do banco de dados - Testando no site oficial")
            print(f"✨ Teste concluído com sucesso para: {cpf_titular}")
            return True
            
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


def processar_todos_os_grupos():
    """
    Processa todos os grupos do dataframe e executa os testes
    """
    print("🔍 Iniciando processamento do dataframe...")
    print(f"📊 Total de linhas no dataframe: {len(dados_limpos)}")
    
    # Processar dataframe e agrupar por titular
    grupos = processar_dataframe(dados_limpos)
    print(f"👥 Total de grupos (titulares) encontrados: {len(grupos)}")
    
    resultados = []
    
    for i, grupo in enumerate(grupos):
        print(f"\n{'='*60}")
        print(f"🔄 Processando grupo {i + 1}/{len(grupos)}")
        
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
    print(f"🔍 Testando grupo específico: {indice_grupo}")
    
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

def testar_apenas_preenchimento(indice_grupo=0):
    """
    Testa apenas o preenchimento do formulário sem enviar (útil para testes no site oficial)
    """
    print(f"🧪 TESTE DE PREENCHIMENTO - Grupo {indice_grupo}")
    print("="*60)
    
    # Limpar dataframe
    dados_limpos = limpar_dataframe(dados)
    
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
    
    # Executar teste (sem envio)
    runner = EFDTestRunner()
    try:
        print(f"\n🔍 Iniciando teste de preenchimento para: {dados_teste.get('cpf', 'N/A')}")
        
        # Navegar para formulário
        if not runner.navegar_para_formulario():
            return False
        
        # Preencher dados iniciais
        if not runner.preencher_dados_iniciais(
            data=dados_teste.get('data'),
            cpf=dados_teste.get('cpf')
        ):
            return False
        
        # Continuar para próxima etapa
        if not runner.continuar_para_proxima_etapa():
            return False
        
        # Adicionar dependentes (se houver)
        dependentes = dados_teste.get('dependentes', [])
        for dep in dependentes:
            if not runner.adicionar_dependente(
                cpf_dependente=dep.get('cpf'),
                relacao=dep.get('relacao'),
                agregado_outros=dep.get('agregado_outros')
            ):
                return False
        
        # Adicionar planos de saúde
        planos = dados_teste.get('planos_saude', [])
        for plano in planos:
            if not runner.adicionar_plano_saude(
                operadora=plano.get('cnpj'),
                valor=plano.get('valor')
            ):
                return False
        
        # Adicionar informações dos dependentes (se houver)
        info_dependentes = dados_teste.get('info_dependentes', [])
        for info in info_dependentes:
            if not runner.adicionar_informacao_dependente(
                cpf_dependente=info.get('cpf'),
                valor=info.get('valor')
            ):
                return False
        
        print(f"\n✅ PREENCHIMENTO CONCLUÍDO COM SUCESSO!")
        print(f"⚠️ Formulário preenchido mas NÃO enviado (função desativada)")
        print(f"💡 Você pode verificar manualmente o formulário no navegador")
        
        # Manter o navegador aberto para verificação manual
        input("\n⏸️ Pressione ENTER para fechar o navegador...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste de preenchimento: {str(e)}")
        runner.tirar_screenshot(f"erro_preenchimento_{dados_teste.get('cpf', 'unknown')}.png")
        return False
    finally:
        runner.close_driver()

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
