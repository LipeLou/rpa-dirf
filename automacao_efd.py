"""
Automação EFD-REINF - Receita Federal
Sistema para automatizar preenchimento de formulários
"""

# Imports
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import time
import random
import pandas as pd
import os
import sys
import platform
import sqlite3
from datetime import datetime
import pyautogui
from PIL import Image
import traceback

# Importar configurações
from config import *

# Configurar encoding UTF-8 para Windows
if platform.system() == "Windows":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURAÇÕES PYAUTOGUI
# ============================================================

# Configurar PyAutoGUI para segurança e performance
pyautogui.FAILSAFE = PYAUTOGUI_FAILSAFE
pyautogui.PAUSE = PYAUTOGUI_PAUSE

# Detectar sistema operacional para configurações específicas
SISTEMA_OPERACIONAL = platform.system()

# Mapeamento de dependências do Excel para valores do formulário
MAPEAMENTO_DEPENDENCIAS = {
    'TITULAR': None,  # Titular não é dependente
    'ESPOSA': '1',    # Cônjuge
    'ESPOSO': '1',    # Cônjuge
    'COMPANHEIRO(A)': '2',  # Companheiro(a) com o(a) qual tenha filho ou viva há mais de 5 (cinco) anos ou possua declaração de união estável
    'COMPANHEIRO': '2',
    'COMPANHEIRA': '2',
    'FILHA': '3',     # Filho(a) ou enteado(a)
    'FILHO': '3',
    'MAE': '9',       # Pais, avós e bisavós
    'MÃE': '9',
    'MAMAE': '9',
    'MAMÃE': '9',
    'PAI': '9',
    'AGREGADO': '99', # Agregado/Outros
    'OUTRA DEPENDENCIA': '99',
    'OUTRA DEPENDÊNCIA': '99',
    'SOGRO': '99',
    'SOGRA': '99'
}

# ============================================================
# CLASSE PRINCIPAL
# ============================================================

class AutomacaoEFD:
    """
    Classe principal para automação completa do EFD-REINF com assinatura eletrônica.
    
    Esta classe gerencia todo o processo de automação, incluindo:
    - Configuração do navegador Chrome
    - Preenchimento automático de formulários
    - Sistema de checkpoints para controle de progresso
    - Assinatura eletrônica automatizada (Métodos A e B)
    - Detecção automática de confirmações de sucesso
    - Navegação automática entre CPFs
    
    Attributes:
        driver (webdriver.Chrome): Instância do navegador Chrome
        cpf_titular_atual (str): CPF do titular sendo processado atualmente
        nome_titular_atual (str): Nome do titular sendo processado
        verificar_dados_manual (bool): Se deve pausar para verificação manual
        metodo_assinatura (int): Método de assinatura (1=teclas, 2=mouse)
        coordenadas_mouse_metodo_b (tuple): Coordenadas (x,y) para método B
    """
    
    def __init__(self):
        """
        Inicializa a automação configurando navegador e banco de dados.
        
        Configura:
        - Chrome com perfil dedicado e proteções anti-detecção
        - Banco de dados SQLite para checkpoints
        - Configurações padrão (verificação manual = True, método A)
        """
        self.driver = None
        self.cpf_titular_atual = None
        self.nome_titular_atual = None
        self.verificar_dados_manual = VERIFICACAO_MANUAL_PADRAO  # Por padrão, verificar dados manualmente
        self.metodo_assinatura = METODO_ASSINATURA_PADRAO  # Por padrão, usar método A
        self.coordenadas_mouse_metodo_b = COORDENADAS_MOUSE_METODO_B  # Carregar do config
        self.inicializar_banco_dados()
        self.configurar_chrome()
    
    def configurar_chrome(self):
        """
        Configura e abre uma instância do Chrome otimizada para automação.
        
        Configurações aplicadas:
        - Perfil dedicado em 'chrome_efd/' para isolamento
        - Proteções anti-detecção com undetected-chromedriver
        - Selenium stealth para mascarar automação
        - Configurações de performance e estabilidade
        
        Raises:
            Exception: Se não conseguir inicializar o Chrome
        """
        print("\n" + "="*60)
        print("🔧 CONFIGURANDO CHROME")
        print("="*60)
        
        print("\n✅ Usando perfil DEDICADO de automação")
        options = uc.ChromeOptions()
        
        # Usar perfil DEDICADO
        profile_dir = os.path.join(os.getcwd(), CHROME_PROFILE_DIR)
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
            print("📁 Perfil criado")
        
        options.add_argument(f'--user-data-dir={profile_dir}')
        
        # Adicionar argumentos do Chrome do config
        for arg in CHROME_ARGS:
            options.add_argument(arg)
        
        options.add_argument('--start-maximized')
        
        print("🚀 Abrindo Chrome...")
        # Especificar versão do Chrome para compatibilidade do ChromeDriver
        self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=CHROME_VERSION)
        
        # Aplicar proteção anti-detecção
        stealth(self.driver,
            languages=["pt-BR", "pt"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        
        print("✅ Chrome aberto!")
    
    def abrir_site(self):
        """Abre o site da Receita Federal"""
        print(f"🌐 Acessando: {URL_BASE}")
        self.driver.get(URL_BASE)
        print("✅ Site carregado!")
    
    def aguardar_login(self):
        """Aguarda o usuário fazer login e navegar até o formulário"""
        print("\n" + "="*60)
        print("🔐 ETAPA: NAVEGAÇÃO MANUAL ATÉ O FORMULÁRIO")
        print("="*60)
        print("\n📋 CLIQUE NOS BOTÕES MANUALMENTE:")
        print("   1. Navegue pelos menus do site")
        print("   2. Clique nos botões necessários")
        print("   3. Chegue até a TELA DO FORMULÁRIO")
        print("\n⚠️ IMPORTANTE - Os 3 campos devem estar VISÍVEIS na tela:")
        print("   ✓ Campo 'Período de Apuração' (MM/AAAA)")
        print("   ✓ Campo 'CNPJ' (00.000.000/0000-00)")
        print("   ✓ Campo 'CPF do Beneficiário' (000.000.000-00)")
        print("\n⚠️ SÓ PRESSIONE ENTER QUANDO VER OS 3 CAMPOS!")
        print("   → URL permanecerá a mesma (página dinâmica)")
        print("   → Código aguardará até 15s o formulário carregar")
        print("   → Depois preenche automaticamente!")
        print("="*60)
        try:
            input("\n✅ VÊ OS 3 CAMPOS NA TELA? Pressione ENTER para automação...\n")
        except (EOFError, KeyboardInterrupt):
            print(f"\n⚠️ Executando via script - aguardando {TEMPO_ESPERA_SCRIPT}s...")
            time.sleep(TEMPO_ESPERA_SCRIPT)
    
    def inspecionar_pagina(self):
        """Permite inspecionar a página atual para debug"""
        print("\n" + "="*60)
        print("🔍 INSPEÇÃO DA PÁGINA")
        print("="*60)
        print(f"URL: {self.driver.current_url}")
        print(f"Título: {self.driver.title}")
        
        # Listar todos os inputs
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        print(f"\n📋 CAMPOS INPUT ENCONTRADOS ({len(inputs)}):")
        
        for i, inp in enumerate(inputs):
            try:
                id_attr = inp.get_attribute("id") or "sem-id"
                name_attr = inp.get_attribute("name") or "sem-name"
                placeholder = inp.get_attribute("placeholder") or "sem-placeholder"
                tipo = inp.get_attribute("type") or "text"
                print(f"   {i+1:2d}. ID: '{id_attr}' | Name: '{name_attr}' | Placeholder: '{placeholder}' | Type: '{tipo}'")
            except:
                print(f"   {i+1:2d}. [erro ao ler atributos]")
        
        # Listar todos os botões
        botoes = self.driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 BOTÕES ENCONTRADOS ({len(botoes)}):")
        
        for i, btn in enumerate(botoes):
            try:
                texto = btn.text or "sem-texto"
                id_attr = btn.get_attribute("id") or "sem-id"
                tipo = btn.get_attribute("type") or "button"
                print(f"   {i+1:2d}. Texto: '{texto}' | ID: '{id_attr}' | Type: '{tipo}'")
            except:
                print(f"   {i+1:2d}. [erro ao ler atributos]")
        
        print("="*60)
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            print("\n🔒 Fechando Chrome...")
            self.driver.quit()
            print("✅ Chrome fechado!")
    
    # ============================================================
    # FUNÇÕES DE AUTOMAÇÃO (a serem implementadas)
    # ============================================================
    
    def delay_humano(self, min_sec=INTERVALO_ESPERA_MIN, max_sec=INTERVALO_ESPERA_MAX):
        """Adiciona delay aleatório para simular comportamento humano"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def digitar_devagar(self, elemento, texto):
        """Digita texto caractere por caractere"""
        for char in str(texto):
            elemento.send_keys(char)
            time.sleep(random.uniform(INTERVALO_DIGITACAO_MIN, INTERVALO_DIGITACAO_MAX))
    
    def formatar_valor(self, valor):
        """Formata um valor para 2 casas decimais no padrão brasileiro (vírgula)"""
        try:
            if isinstance(valor, str):
                # Remover caracteres não numéricos exceto vírgula e ponto
                valor_limpo = ''.join(c for c in valor if c.isdigit() or c in [',', '.'])
                # Substituir vírgula por ponto para conversão
                valor_limpo = valor_limpo.replace(',', '.')
                valor_float = float(valor_limpo)
            else:
                valor_float = float(valor)
            
            # Arredondar para 2 casas decimais
            valor_arredondado = round(valor_float, 2)
            
            # Formatar com 2 casas decimais e vírgula
            return f"{valor_arredondado:.2f}".replace('.', ',')
        except (ValueError, TypeError):
            return '0,00'
    
    def valor_eh_zero_ou_nulo(self, valor):
        """
        Verifica se um valor é zero ou nulo (sem valor).
        
        Args:
            valor: Valor a ser verificado (pode ser str, float, int, None, etc.)
        
        Returns:
            bool: True se o valor for zero ou nulo, False caso contrário
        """
        # Se for None ou string vazia
        if valor is None or (isinstance(valor, str) and valor.strip() == ''):
            return True
        
        # Tentar converter para float e verificar se é zero
        try:
            if isinstance(valor, str):
                # Remover caracteres não numéricos exceto vírgula e ponto
                valor_limpo = ''.join(c for c in valor if c.isdigit() or c in [',', '.'])
                # Substituir vírgula por ponto para conversão
                valor_limpo = valor_limpo.replace(',', '.')
                valor_float = float(valor_limpo)
            else:
                valor_float = float(valor)
            
            # Verificar se é zero (com tolerância para pequenas diferenças de ponto flutuante)
            return abs(valor_float) < 0.01
        except (ValueError, TypeError):
            # Se não conseguir converter, considerar como nulo
            return True

    def salvar_coordenadas_config(self, coordenadas):
        """Salva as coordenadas no arquivo config.py"""
        try:
            # Ler o arquivo atual
            with open('config.py', 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Substituir a linha das coordenadas
            if coordenadas:
                nova_linha = f"COORDENADAS_MOUSE_METODO_B = {coordenadas}"
            else:
                nova_linha = "COORDENADAS_MOUSE_METODO_B = None"
            
            # Encontrar e substituir a linha
            linhas = conteudo.split('\n')
            for i, linha in enumerate(linhas):
                if linha.startswith('COORDENADAS_MOUSE_METODO_B'):
                    linhas[i] = nova_linha
                    break
            
            # Salvar o arquivo
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(linhas))
            
            print(f"💾 Coordenadas salvas no config.py: {coordenadas}")
            return True
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar coordenadas no config.py: {e}")
            return False
    
    def mapear_dependencia(self, dependencia_dataframe):
        """Mapeia a dependência do Excel para o valor do formulário"""
        dependencia_upper = str(dependencia_dataframe).strip().upper()
        
        # Buscar mapeamento exato
        if dependencia_upper in MAPEAMENTO_DEPENDENCIAS:
            return MAPEAMENTO_DEPENDENCIAS[dependencia_upper]
        
        # Buscar mapeamento parcial (para variações)
        for key, value in MAPEAMENTO_DEPENDENCIAS.items():
            if key in dependencia_upper or dependencia_upper in key:
                return value
        
        # Se não encontrar, usar "Agregado/Outros" como padrão
        print(f"⚠️ Dependência não mapeada: '{dependencia_dataframe}' - usando '99' (Agregado/Outros)")
        return '99'
    
    def inicializar_banco_dados(self):
        """Inicializa o banco de dados SQLite para checkpoint"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            # Criar tabela de progresso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progresso_efd (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf_titular TEXT NOT NULL,
                    nome_titular TEXT,
                    etapa_atual TEXT NOT NULL,
                    status TEXT NOT NULL,
                    dados_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    observacoes TEXT
                )
            ''')
            
            # Criar tabela de dependentes processados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dependentes_processados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf_titular TEXT NOT NULL,
                    cpf_dependente TEXT NOT NULL,
                    relacao TEXT,
                    descricao_agregado TEXT,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Criar tabela de planos processados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS planos_processados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf_titular TEXT NOT NULL,
                    cnpj_operadora TEXT NOT NULL,
                    valor_titular TEXT,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Criar tabela de informações dos dependentes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS info_dependentes_processados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf_titular TEXT NOT NULL,
                    cpf_dependente TEXT NOT NULL,
                    valor_dependente TEXT,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Banco de dados inicializado")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            return False
    
    def salvar_checkpoint(self, cpf_titular, nome_titular, etapa, status, dados=None, observacoes=None):
        """Salva checkpoint do progresso"""
        try:
            import json
            
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            dados_json = json.dumps(dados) if dados else None
            
            cursor.execute('''
                INSERT INTO progresso_efd 
                (cpf_titular, nome_titular, etapa_atual, status, dados_json, observacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cpf_titular, nome_titular, etapa, status, dados_json, observacoes))
            
            conn.commit()
            conn.close()
            print(f"💾 Checkpoint salvo: {etapa} - {status}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar checkpoint: {e}")
            return False
    
    def salvar_dependente_processado(self, cpf_titular, cpf_dependente, relacao, descricao_agregado, status):
        """Salva dependente processado"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO dependentes_processados 
                (cpf_titular, cpf_dependente, relacao, descricao_agregado, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cpf_titular, cpf_dependente, relacao, descricao_agregado, status, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar dependente: {e}")
            return False
    
    def salvar_plano_processado(self, cpf_titular, cnpj_operadora, valor_titular, status):
        """Salva plano de saúde processado"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO planos_processados 
                (cpf_titular, cnpj_operadora, valor_titular, status, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (cpf_titular, cnpj_operadora, valor_titular, status, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar plano: {e}")
            return False

    def verificar_grupo_completamente_processado(self, cpf_titular):
        """Verifica se um grupo foi completamente processado (chegou até o final)"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            # Verificar se existe checkpoint de "grupo_completo" com sucesso
            cursor.execute('''
                SELECT COUNT(*) FROM progresso_efd 
                WHERE cpf_titular = ? AND etapa_atual = 'grupo_completo' AND status = 'sucesso'
            ''', (cpf_titular,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            print(f"❌ Erro ao verificar grupo completo: {e}")
            return False

    def verificar_ultimo_status_pulado(self, cpf_titular):
        """Verifica se o último checkpoint do CPF foi 'pulado' (ex: CPF já lançado)"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            # Buscar o último checkpoint deste CPF
            cursor.execute('''
                SELECT etapa_atual, status FROM progresso_efd 
                WHERE cpf_titular = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (cpf_titular,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                etapa, status = resultado
                return status == 'pulado'
            
            return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar último status: {e}")
            return False

    def limpar_dados_parciais_grupo(self, cpf_titular):
        """Remove dados parciais de um grupo que não foi completado"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            # Remover dependentes parciais
            cursor.execute('DELETE FROM dependentes_processados WHERE cpf_titular = ?', (cpf_titular,))
            
            # Remover planos parciais  
            cursor.execute('DELETE FROM planos_processados WHERE cpf_titular = ?', (cpf_titular,))
            
            # Remover informações de dependentes parciais
            cursor.execute('DELETE FROM info_dependentes_processados WHERE cpf_titular = ?', (cpf_titular,))
            
            # Remover checkpoints parciais (manter apenas se grupo foi completamente processado)
            cursor.execute('''
                DELETE FROM progresso_efd 
                WHERE cpf_titular = ? AND NOT (etapa_atual = 'grupo_completo' AND status = 'sucesso')
            ''', (cpf_titular,))
            
            conn.commit()
            conn.close()
            
            print(f"🧹 Dados parciais removidos para CPF: {cpf_titular}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao limpar dados parciais: {e}")
            return False
    
    def salvar_info_dependente_processado(self, cpf_titular, cpf_dependente, valor_dependente, status):
        """Salva informação de dependente processado"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO info_dependentes_processados 
                (cpf_titular, cpf_dependente, valor_dependente, status)
                VALUES (?, ?, ?, ?)
            ''', (cpf_titular, cpf_dependente, valor_dependente, status))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar info dependente: {e}")
            return False
    
    def verificar_progresso(self, cpf_titular):
        """Verifica o progresso atual de um titular"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT etapa_atual, status, timestamp, observacoes
                FROM progresso_efd 
                WHERE cpf_titular = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (cpf_titular,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                etapa, status, timestamp, observacoes = resultado
                print(f"📊 Progresso encontrado para {cpf_titular}:")
                print(f"   Etapa: {etapa}")
                print(f"   Status: {status}")
                print(f"   Timestamp: {timestamp}")
                if observacoes:
                    print(f"   Observações: {observacoes}")
                return {'etapa': etapa, 'status': status, 'timestamp': timestamp, 'observacoes': observacoes}
            else:
                print(f"📊 Nenhum progresso encontrado para {cpf_titular}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao verificar progresso: {e}")
            return None
    
    def limpar_progresso(self, cpf_titular=None):
        """Limpa o progresso (todos ou de um titular específico)"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            if cpf_titular:
                cursor.execute('DELETE FROM progresso_efd WHERE cpf_titular = ?', (cpf_titular,))
                cursor.execute('DELETE FROM dependentes_processados WHERE cpf_titular = ?', (cpf_titular,))
                cursor.execute('DELETE FROM planos_processados WHERE cpf_titular = ?', (cpf_titular,))
                cursor.execute('DELETE FROM info_dependentes_processados WHERE cpf_titular = ?', (cpf_titular,))
                print(f"🗑️ Progresso limpo para {cpf_titular}")
            else:
                cursor.execute('DELETE FROM progresso_efd')
                cursor.execute('DELETE FROM dependentes_processados')
                cursor.execute('DELETE FROM planos_processados')
                cursor.execute('DELETE FROM info_dependentes_processados')
                print("🗑️ Todo progresso limpo")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao limpar progresso: {e}")
            return False
    
    def mostrar_status_checkpoint(self):
        """Mostra o status atual do checkpoint"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            # Contar registros por tabela
            cursor.execute('SELECT COUNT(*) FROM progresso_efd')
            total_progresso = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM dependentes_processados')
            total_dependentes = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM planos_processados')
            total_planos = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM info_dependentes_processados')
            total_info_dependentes = cursor.fetchone()[0]
            
            # Últimos 5 registros de progresso
            cursor.execute('''
                SELECT cpf_titular, nome_titular, etapa_atual, status, timestamp 
                FROM progresso_efd 
                ORDER BY timestamp DESC 
                LIMIT 5
            ''')
            ultimos_progressos = cursor.fetchall()
            
            conn.close()
            
            print(f"\n📊 STATUS DO CHECKPOINT")
            print(f"{'='*60}")
            print(f"Total de registros de progresso: {total_progresso}")
            print(f"Total de dependentes processados: {total_dependentes}")
            print(f"Total de planos processados: {total_planos}")
            print(f"Total de informações de dependentes: {total_info_dependentes}")
            
            if ultimos_progressos:
                print(f"\nÚltimos 5 progressos:")
                for registro in ultimos_progressos:
                    cpf, nome, etapa, status, timestamp = registro
                    print(f"  {cpf} | {nome} | {etapa} | {status} | {timestamp}")
            
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Erro ao mostrar status: {e}")
    
    def gerar_planilha_visualizacao(self):
        """Gera planilha Excel para visualização do banco de dados"""
        try:
            print("\n📊 Gerando planilha de visualização...")
            
            conn = sqlite3.connect(BANCO_DADOS)
            
            # Buscar dados de progresso
            df_progresso = pd.read_sql_query('''
                SELECT 
                    cpf_titular,
                    nome_titular,
                    etapa_atual,
                    status,
                    timestamp,
                    observacoes
                FROM progresso_efd 
                ORDER BY timestamp DESC
            ''', conn)
            
            # Buscar dependentes processados
            df_dependentes = pd.read_sql_query('''
                SELECT 
                    cpf_titular,
                    cpf_dependente,
                    relacao,
                    descricao_agregado,
                    status,
                    timestamp
                FROM dependentes_processados 
                ORDER BY timestamp DESC
            ''', conn)
            
            
            conn.close()
            
            # Criar resumo por CPF
            resumo_cpfs = []
            cpfs_unicos = df_progresso['cpf_titular'].unique()
            
            for cpf in cpfs_unicos:
                dados_cpf = df_progresso[df_progresso['cpf_titular'] == cpf]
                ultimo_status = dados_cpf.iloc[0]  # Mais recente
                
                # Contar dependentes
                total_dependentes = len(df_dependentes[df_dependentes['cpf_titular'] == cpf])
                
                resumo_cpfs.append({
                    'CPF_Titular': cpf,
                    'Nome_Titular': ultimo_status['nome_titular'],
                    'Status_Final': ultimo_status['status'],
                    'Etapa_Atual': ultimo_status['etapa_atual'],
                    'Total_Dependentes': total_dependentes,
                    'Ultima_Atualizacao': ultimo_status['timestamp'],
                    'Observacoes': ultimo_status['observacoes']
                })
            
            df_resumo = pd.DataFrame(resumo_cpfs)
            
            # Gerar arquivo Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"visualizacao_checkpoint_{timestamp}.xlsx"
            
            with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
                # Aba Resumo
                df_resumo.to_excel(writer, sheet_name='Resumo_CPFs', index=False)
                
                # Aba Progresso Detalhado
                df_progresso.to_excel(writer, sheet_name='Progresso_Detalhado', index=False)
                
                # Aba Dependentes
                df_dependentes.to_excel(writer, sheet_name='Dependentes', index=False)
                
                # Aba Estatísticas
                stats = {
                    'Metrica': [
                        'Total de CPFs',
                        'CPFs com Sucesso',
                        'CPFs Pulados',
                        'CPFs com Erro',
                        'Total de Dependentes'
                    ],
                    'Valor': [
                        len(cpfs_unicos),
                        len(df_resumo[df_resumo['Status_Final'] == 'sucesso']),
                        len(df_resumo[df_resumo['Status_Final'] == 'pulado']),
                        len(df_resumo[df_resumo['Status_Final'] == 'erro']),
                        len(df_dependentes)
                    ]
                }
                df_stats = pd.DataFrame(stats)
                df_stats.to_excel(writer, sheet_name='Estatisticas', index=False)
            
            print(f"✅ Planilha gerada: {nome_arquivo}")
            print(f"📊 {len(cpfs_unicos)} CPFs processados")
            print(f"📋 {len(df_resumo)} registros no resumo")
            
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao gerar planilha: {e}")
            return None
    
    def tratar_erro_cpf_ja_lancado(self, erros_encontrados):
        """Trata especificamente o erro de CPF já lançado"""
        try:
            # Verificar se é o erro específico de CPF já lançado
            erro_cpf_ja_lancado = False
            for erro in erros_encontrados:
                if "inclusão não permitida" in erro.lower() and "evento ativo" in erro.lower():
                    erro_cpf_ja_lancado = True
                    break
            
            if erro_cpf_ja_lancado:
                print(f"\n🚫 ERRO ESPECÍFICO DETECTADO:")
                print(f"   CPF {self.cpf_titular_atual} já foi lançado para este período!")
                print(f"   ⏭️ Pulando para o próximo grupo...")
                
                # Salvar checkpoint específico para CPF já lançado
                self.salvar_checkpoint(
                    self.cpf_titular_atual,
                    self.nome_titular_atual,
                    "cpf_ja_lancado",
                    "pulado",
                    observacoes="CPF já foi lançado para este período - pulando para próximo grupo"
                )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erro ao tratar CPF já lançado: {e}")
            return False
    
    def preencher_dados_iniciais(self, cpf_titular, nome_titular=None):
        """
        Preenche os 3 campos iniciais e clica em Continuar
        
        Args:
            cpf_titular: CPF do titular a ser preenchido
            nome_titular: Nome do titular (opcional)
        """
        print("\n📝 Preenchendo dados iniciais...")
        
        # Definir titular atual para checkpoint
        self.cpf_titular_atual = cpf_titular
        self.nome_titular_atual = nome_titular or "Titular"
        
        # Salvar checkpoint - iniciando preenchimento
        self.salvar_checkpoint(
            cpf_titular, 
            nome_titular, 
            "dados_iniciais", 
            "iniciando",
            observacoes="Iniciando preenchimento dos dados iniciais"
        )
        
        try:
            # DEBUG: Ver estado da página
            print(f"\n🔍 DEBUG:")
            print(f"   URL: {self.driver.current_url}")
            print(f"   Título: {self.driver.title}")
            
            # Verificar iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"   Iframes encontrados: {len(iframes)}")
            
            # Se tiver iframe, entrar nele
            if len(iframes) > 0:
                print(f"   ⚠️ PÁGINA TEM IFRAME! Entrando no primeiro iframe...")
                self.driver.switch_to.frame(0)
                print(f"   ✅ Dentro do iframe")
            
            # Aguardar e procurar elemento
            print("   ⏳ Aguardando formulário carregar (15s)...")
            
            # Tentar encontrar por múltiplos métodos
            elemento_encontrado = False
            tentativas = [
                ("ID", By.ID, "periodo_apuracao"),
                ("data-testid", By.CSS_SELECTOR, '[data-testid="periodo_apuracao"]'),
                ("placeholder", By.CSS_SELECTOR, 'input[placeholder="MM/AAAA"]'),
            ]
            
            for nome, metodo, seletor in tentativas:
                try:
                    print(f"   Tentando encontrar por {nome}: {seletor}")
                    WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                        EC.presence_of_element_located((metodo, seletor))
                    )
                    print(f"   ✅ Encontrado por {nome}!")
                    elemento_encontrado = True
                    break
                except:
                    print(f"   ❌ Não encontrado por {nome}")
                    continue
            
            if not elemento_encontrado:
                # Mostrar o que TEM na página
                print("\n   📋 ELEMENTOS INPUT NA PÁGINA:")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                print(f"   Total: {len(inputs)}")
                for i, inp in enumerate(inputs[:15]):
                    try:
                        id_attr = inp.get_attribute("id") or "sem-id"
                        testid = inp.get_attribute("data-testid") or "sem-testid"
                        placeholder = inp.get_attribute("placeholder") or "sem-placeholder"
                        print(f"      {i+1}. ID='{id_attr}' | testid='{testid}' | placeholder='{placeholder}'")
                    except:
                        pass
                
                print("\n   ❌ FORMULÁRIO NÃO ENCONTRADO!")
                print("   ⚠️ Você pressionou ENTER com os 3 campos VISÍVEIS na tela?")
                return False
            
            print("   ✅ Formulário detectado!")
            self.delay_humano(0.5, 1.0)
            
            # CAMPO 1: Período de Apuração
            print("   📅 Preenchendo Período de Apuração...")
            campo_data = self.driver.find_element(By.ID, "periodo_apuracao")
            campo_data.clear()
            self.delay_humano(0.2, 0.5)
            self.digitar_devagar(campo_data, PERIODO_APURACAO)
            print(f"   ✅ Data: {PERIODO_APURACAO}")
            self.delay_humano(0.5, 1.0)
            
            # CAMPO 2: CNPJ
            print("   🏢 Preenchendo CNPJ...")
            campo_cnpj = self.driver.find_element(By.ID, "insc_estabelecimento")
            campo_cnpj.clear()
            self.delay_humano(0.2, 0.5)
            self.digitar_devagar(campo_cnpj, CNPJ_EMPRESA)
            print(f"   ✅ CNPJ: {CNPJ_EMPRESA}")
            self.delay_humano(0.5, 1.0)
            
            # CAMPO 3: CPF do Beneficiário
            print(f"   👤 Preenchendo CPF do Beneficiário...")
            campo_cpf = self.driver.find_element(By.ID, "cpf_beneficiario")
            campo_cpf.clear()
            self.delay_humano(0.2, 0.5)
            self.digitar_devagar(campo_cpf, cpf_titular)
            print(f"   ✅ CPF: {cpf_titular}")
            self.delay_humano(0.8, 1.5)
            
            # BOTÃO: Continuar será clicado na função continuar_para_proxima_etapa()
            print("   🔘 Botão 'Continuar' será clicado na próxima etapa...")
            self.delay_humano(0.5, 1.0)
            
            print("\n✅ Dados iniciais preenchidos com sucesso!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro ao preencher dados iniciais: {e}")
            return False
    
    def verificar_erros_primeira_etapa(self):
        """Verifica se há erros na primeira etapa (spans de aviso)"""
        try:
            print("\n🔍 Verificando erros na primeira etapa...")
            
            # Procurar por spans de erro/aviso
            spans_erro = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'erro') or contains(@class, 'error') or contains(@class, 'aviso') or contains(@class, 'warning') or contains(@class, 'alert')]")
            
            # Procurar por divs de erro
            divs_erro = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'erro') or contains(@class, 'error') or contains(@class, 'aviso') or contains(@class, 'warning') or contains(@class, 'alert')]")
            
            # Procurar especificamente pelo componente de mensagem de alerta
            mensagens_alerta = self.driver.find_elements(By.XPATH, "//app-reinf-mensagens-alerta//div[@class='message alert']")
            
            # Procurar por elementos com texto de erro comum
            textos_erro = [
                "CPF já foi lançado",
                "já foi lançado",
                "duplicado",
                "inválido",
                "erro",
                "não encontrado",
                "campo obrigatório",
                "Inclusão não permitida",
                "Existe um evento ativo",
                "CPF do beneficiário",
                "mesmo período de apuração"
            ]
            
            erros_encontrados = []
            
            # Verificar spans
            for span in spans_erro:
                texto = span.text.strip()
                if texto and any(palavra in texto.lower() for palavra in textos_erro):
                    erros_encontrados.append(f"SPAN: {texto}")
            
            # Verificar divs
            for div in divs_erro:
                texto = div.text.strip()
                if texto and any(palavra in texto.lower() for palavra in textos_erro):
                    erros_encontrados.append(f"DIV: {texto}")
            
            # Verificar mensagens de alerta específicas
            for mensagem in mensagens_alerta:
                if mensagem.is_displayed():
                    # Procurar pela descrição da mensagem
                    try:
                        descricao = mensagem.find_element(By.CSS_SELECTOR, '[data-testid*="mensagem_descricao"]')
                        texto_descricao = descricao.text.strip()
                        if texto_descricao:
                            erros_encontrados.append(f"ALERTA: {texto_descricao}")
                    except:
                        # Se não encontrar a descrição, pegar o texto completo da mensagem
                        texto_completo = mensagem.text.strip()
                        if texto_completo and any(palavra in texto_completo.lower() for palavra in textos_erro):
                            erros_encontrados.append(f"ALERTA: {texto_completo}")
            
            # Procurar por elementos com texto de erro específico
            for texto_erro in textos_erro:
                elementos = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{texto_erro}')]")
                for elemento in elementos:
                    if elemento.text.strip() and elemento.is_displayed():
                        erros_encontrados.append(f"TEXTO: {elemento.text.strip()}")
            
            if erros_encontrados:
                # Tratar erro específico de CPF já lançado
                if self.tratar_erro_cpf_ja_lancado(erros_encontrados):
                    # Se for CPF já lançado, não precisa salvar checkpoint adicional
                    return False
                
                # Salvar checkpoint de erro genérico
                self.salvar_checkpoint(
                    self.cpf_titular_atual,
                    self.nome_titular_atual,
                    "erro_primeira_etapa",
                    "erro",
                    observacoes=f"Erros: {'; '.join(erros_encontrados)}"
                )
                return False
            else:
                print("✅ Nenhum erro encontrado na primeira etapa")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao verificar erros: {e}")
            return False
    
    def verificar_segunda_etapa_carregou(self):
        """Verifica se a segunda etapa carregou corretamente"""
        try:
            print("\n🔍 Verificando se segunda etapa carregou...")
            
            # Aguardar um pouco para a página processar
            time.sleep(TEMPO_PROCESSAMENTO_PAGINA)
            
            # Verificar se ainda estamos na primeira etapa (campos iniciais ainda visíveis)
            campos_primeira_etapa = [
                (By.ID, "periodo_apuracao"),
                (By.ID, "insc_estabelecimento"),
                (By.ID, "cpf_beneficiario")
            ]
            
            primeira_etapa_ainda_visivel = False
            for metodo, seletor in campos_primeira_etapa:
                try:
                    elemento = self.driver.find_element(metodo, seletor)
                    if elemento.is_displayed():
                        primeira_etapa_ainda_visivel = True
                        break
                except:
                    continue
            
            if primeira_etapa_ainda_visivel:
                print("⚠️ Primeira etapa ainda está visível - pode ter havido erro")
                return False
            
            # Verificar se elementos da segunda etapa estão presentes
            elementos_segunda_etapa = [
                (By.ID, "BotaoInclusaoDiv_ideDep"),  # Botão adicionar dependente
                (By.ID, "BotaoInclusaoDiv_ideOpSaude"),  # Botão adicionar plano
                (By.XPATH, "//button[contains(@id, 'BotaoInclusaoDiv')]")  # Qualquer botão de inclusão
            ]
            
            segunda_etapa_carregou = False
            for metodo, seletor in elementos_segunda_etapa:
                try:
                    elemento = self.driver.find_element(metodo, seletor)
                    if elemento.is_displayed():
                        segunda_etapa_carregou = True
                        print(f"✅ Segunda etapa carregou - elemento encontrado: {seletor}")
                        break
                except:
                    continue
            
            if not segunda_etapa_carregou:
                print("❌ Segunda etapa não carregou - elementos não encontrados")
                return False
            
            # Verificar se há mensagens de sucesso ou confirmação
            mensagens_sucesso = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'sucesso') or contains(text(), 'Sucesso') or contains(text(), 'confirmado') or contains(text(), 'Confirmado')]")
            if mensagens_sucesso:
                for msg in mensagens_sucesso:
                    if msg.is_displayed():
                        print(f"✅ Mensagem de sucesso: {msg.text}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar segunda etapa: {e}")
            return False
    
    def continuar_para_proxima_etapa(self):
        """Clica no botão Continuar e verifica se passou para a próxima etapa"""
        try:
            print("\n🔄 Continuando para próxima etapa...")
            
            # Aguardar botão "Continuar" aparecer
            WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="botao_continuar"]'))
            )
            
            # Clicar em Continuar
            botao_continuar = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="botao_continuar"]')
            botao_continuar.click()
            print("✅ Clicado em Continuar")
            
            # Aguardar um pouco para a página processar
            time.sleep(TEMPO_PROCESSAMENTO_PAGINA)
            
            # Verificar se há erros na primeira etapa
            if not self.verificar_erros_primeira_etapa():
                print("❌ Erros encontrados na primeira etapa - não foi possível continuar")
                return False
            
            # Verificar se a segunda etapa carregou
            if not self.verificar_segunda_etapa_carregou():
                print("❌ Segunda etapa não carregou corretamente")
                return False
            
            # Salvar checkpoint de sucesso
            self.salvar_checkpoint(
                self.cpf_titular_atual,
                self.nome_titular_atual,
                "segunda_etapa_carregada",
                "sucesso",
                observacoes="Segunda etapa carregada com sucesso"
            )
            
            print("✅ Segunda etapa carregada com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao continuar para próxima etapa: {e}")
            self.salvar_checkpoint(
                self.cpf_titular_atual,
                self.nome_titular_atual,
                "erro_continuar_etapa",
                "erro",
                observacoes=f"Erro: {str(e)}"
            )
            return False
    
    def adicionar_dependente(self, cpf_dependente, relacao_valor, agregado_outros=None):
        """Adiciona um dependente ao formulário"""
        try:
            # Verificar se CPF é válido
            if not cpf_dependente or str(cpf_dependente).strip() == '' or str(cpf_dependente).strip().lower() == 'nan':
                print(f"⚠️ Pulando dependente - CPF inválido: {cpf_dependente}")
                return True
            
            print(f"\n👥 Adicionando dependente: {cpf_dependente}")
            
            # Salvar checkpoint - iniciando dependente
            self.salvar_checkpoint(
                self.cpf_titular_atual, 
                self.nome_titular_atual, 
                "adicionando_dependente", 
                "em_andamento",
                observacoes=f"CPF: {cpf_dependente}, Relação: {relacao_valor}"
            )
            
            # Clicar no botão "Adicionar dependente"
            try:
                botao_adicionar = self.driver.find_element(By.ID, "BotaoInclusaoDiv_ideDep")
                botao_adicionar.click()
                print("✅ Modal de dependente aberto")
            except Exception as e:
                print(f"❌ Erro ao clicar no botão adicionar dependente: {e}")
                self.salvar_dependente_processado(self.cpf_titular_atual, cpf_dependente, relacao_valor, agregado_outros, "erro")
                return False
            
            # Aguardar modal carregar
            WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                EC.presence_of_element_located((By.ID, "cpf_dependente"))
            )
            
            # Preencher CPF do dependente
            try:
                campo_cpf = self.driver.find_element(By.ID, "cpf_dependente")
                campo_cpf.clear()
                self.digitar_devagar(campo_cpf, cpf_dependente)
                print(f"✅ CPF do dependente preenchido: {cpf_dependente}")
            except Exception as e:
                print(f"❌ Erro ao preencher CPF: {e}")
                self.salvar_dependente_processado(self.cpf_titular_atual, cpf_dependente, relacao_valor, agregado_outros, "erro")
                return False
            
            # Selecionar relação de dependência
            try:
                select_relacao = Select(self.driver.find_element(By.ID, "relacao_dependencia"))
                select_relacao.select_by_value(relacao_valor)
                print(f"✅ Relação selecionada: {relacao_valor}")
            except Exception as e:
                print(f"❌ Erro ao selecionar relação: {e}")
                self.salvar_dependente_processado(self.cpf_titular_atual, cpf_dependente, relacao_valor, agregado_outros, "erro")
                return False
            
            # Se for "Agregado/Outros" (valor 99), preencher campo de descrição
            if relacao_valor == "99" and agregado_outros:
                try:
                    # Aguardar campo de descrição aparecer
                    WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                        EC.presence_of_element_located((By.ID, "descricao_dependencia"))
                    )
                    
                    campo_descricao = self.driver.find_element(By.ID, "descricao_dependencia")
                    campo_descricao.clear()
                    self.digitar_devagar(campo_descricao, agregado_outros)
                    print(f"✅ Descrição da dependência preenchida: {agregado_outros}")
                except Exception as e:
                    print(f"⚠️ Campo de descrição não encontrado: {e}")
            elif relacao_valor == "99":
                print("⚠️ Relação é 'Agregado/Outros' mas não foi fornecida descrição")
            
            # Clicar em Salvar
            try:
                botao_salvar = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="botao_salvar_modal_ide_dep"]')
                botao_salvar.click()
                print("✅ Dependente adicionado")
                
                # Aguardar modal fechar
                WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                    EC.invisibility_of_element_located((By.ID, "cpf_dependente"))
                )
                
                # Salvar checkpoint - dependente adicionado com sucesso
                self.salvar_checkpoint(
                    self.cpf_titular_atual, 
                    self.nome_titular_atual, 
                    "dependente_adicionado", 
                    "sucesso",
                    observacoes=f"CPF: {cpf_dependente} adicionado com sucesso"
                )
                
                # Salvar dependente como processado
                self.salvar_dependente_processado(self.cpf_titular_atual, cpf_dependente, relacao_valor, agregado_outros, "sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao salvar dependente: {e}")
                self.salvar_dependente_processado(self.cpf_titular_atual, cpf_dependente, relacao_valor, agregado_outros, "erro")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar dependente: {e}")
            self.salvar_dependente_processado(self.cpf_titular_atual, cpf_dependente, relacao_valor, agregado_outros, "erro")
            return False
    
    def adicionar_plano_saude(self, cnpj_operadora, valor_titular):
        """Adiciona um plano de saúde ao formulário"""
        try:
            print(f"\n🏥 Adicionando plano de saúde: {cnpj_operadora}")
            
            # Clicar no botão "Adicionar plano de saúde"
            try:
                botao_adicionar = self.driver.find_element(By.ID, "BotaoInclusaoDiv_ideOpSaude")
                botao_adicionar.click()
                print("✅ Modal de plano de saúde aberto")
            except Exception as e:
                print(f"❌ Erro ao clicar no botão adicionar plano de saúde: {e}")
                self.salvar_plano_processado(self.cpf_titular_atual, cnpj_operadora, valor_titular, "erro")
                return False
            
            # Aguardar modal carregar
            WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                EC.presence_of_element_located((By.ID, "cnpj_operadora"))
            )
            
            # Preencher CNPJ da operadora
            try:
                campo_cnpj = self.driver.find_element(By.ID, "cnpj_operadora")
                campo_cnpj.clear()
                self.digitar_devagar(campo_cnpj, cnpj_operadora)
                print(f"✅ CNPJ da operadora preenchido: {cnpj_operadora}")
            except Exception as e:
                print(f"❌ Erro ao preencher CNPJ: {e}")
                self.salvar_plano_processado(self.cpf_titular_atual, cnpj_operadora, valor_titular, "erro")
                return False
            
            # Preencher valor pago pelo titular
            try:
                campo_valor = self.driver.find_element(By.ID, "valor_saude")
                campo_valor.clear()
                self.digitar_devagar(campo_valor, valor_titular)
                print(f"✅ Valor pago pelo titular preenchido: R$ {valor_titular}")
            except Exception as e:
                print(f"❌ Erro ao preencher valor: {e}")
                self.salvar_plano_processado(self.cpf_titular_atual, cnpj_operadora, valor_titular, "erro")
                return False
            
            # Clicar em Salvar
            try:
                botao_salvar = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="botao_salvar_modal_ide_op_saude"]')
                botao_salvar.click()
                print("✅ Plano de saúde adicionado")
                
                # Aguardar modal fechar
                WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                    EC.invisibility_of_element_located((By.ID, "cnpj_operadora"))
                )
                
                # Salvar plano como processado
                self.salvar_plano_processado(self.cpf_titular_atual, cnpj_operadora, valor_titular, "sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao salvar plano de saúde: {e}")
                self.salvar_plano_processado(self.cpf_titular_atual, cnpj_operadora, valor_titular, "erro")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar plano de saúde: {e}")
            self.salvar_plano_processado(self.cpf_titular_atual, cnpj_operadora, valor_titular, "erro")
            return False
    
    def adicionar_informacao_dependente(self, cpf_dependente, valor_dependente):
        """Adiciona informação de dependente (valor)"""
        try:
            if not cpf_dependente or str(cpf_dependente).strip() == '' or str(cpf_dependente).strip().lower() == 'nan':
                print(f"⚠️ Pulando informação do dependente - CPF inválido: {cpf_dependente}")
                return True
            
            print(f"\n💰 Adicionando informação do dependente: {cpf_dependente}")
            
            # Clicar no botão "Adicionar Informações dos Dependentes"
            try:
                botao_adicionar = self.driver.find_element(By.ID, "BotaoInclusaoDiv_infoDependPl_0")
                botao_adicionar.click()
                print("✅ Modal de informações dos dependentes aberto")
            except Exception as e:
                print(f"❌ Erro ao clicar no botão adicionar informações: {e}")
                return False
            
            # Aguardar modal carregar
            WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                EC.presence_of_element_located((By.ID, "c_p_f_do_dependente"))
            )
            
            # Selecionar dependente pelo CPF
            try:
                select_dependente = Select(self.driver.find_element(By.ID, "c_p_f_do_dependente"))
                select_dependente.select_by_value(cpf_dependente)
                print(f"✅ Dependente selecionado: {cpf_dependente}")
            except Exception as e:
                print(f"❌ Erro ao selecionar dependente: {e}")
                return False
            
            # Preencher valor pago pelo dependente
            try:
                campo_valor = self.driver.find_element(By.ID, "valor_saude_plano")
                campo_valor.clear()
                self.digitar_devagar(campo_valor, valor_dependente)
                print(f"✅ Valor pago pelo dependente preenchido: R$ {valor_dependente}")
            except Exception as e:
                print(f"❌ Erro ao preencher valor: {e}")
                return False
            
            # Clicar em Salvar
            try:
                botao_salvar = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="botao_salvar_modal_info_depend_pl"]')
                botao_salvar.click()
                print("✅ Informação do dependente adicionada")
                
                # Aguardar modal fechar
                WebDriverWait(self.driver, TIMEOUT_MODAL).until(
                    EC.invisibility_of_element_located((By.ID, "c_p_f_do_dependente"))
                )
            except Exception as e:
                print(f"❌ Erro ao salvar informação do dependente: {e}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar informação do dependente: {e}")
            return False
    
    def enviar_declaracao(self):
        """Envia a declaração usando o botão 'Concluir e enviar'"""
        try:
            print("📤 Enviando declaração...")
            time.sleep(TEMPO_ANTES_ENVIO)
            wait = WebDriverWait(self.driver, TIMEOUT_WEBDRIVER)
            
            try:
                # Tentar localizar pelo data-testid (preferencial)
                botao_enviar = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="botao_concluir_enviar"]'))
                )
                print("✅ Botão encontrado pelo data-testid")
            except:
                # Fallback: tentar localizar pelo texto do botão
                print("⚠️ Tentando localizar pelo texto...")
                botao_enviar = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Concluir e enviar')]"))
                )
                print("✅ Botão encontrado pelo texto")
            
            # Scroll até o botão para garantir visibilidade
            self.driver.execute_script("arguments[0].scrollIntoView(true);", botao_enviar)
            time.sleep(TEMPO_APOS_SCROLL)
            
            # Clicar no botão
            print("🖱️ Clicando no botão 'Concluir e enviar'...")
            botao_enviar.click()
            
            print("✅ Declaração enviada com sucesso!")
            print("⏳ Aguardando página de confirmação/assinatura...")
            
            # Aguardar a próxima página carregar
            time.sleep(TEMPO_APOS_ENVIO)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar declaração: {e}")
            print("💡 Verifique se o formulário foi totalmente preenchido")
            return False
    
    def aguardar_alerta_sucesso_assinatura(self):
        """Aguarda automaticamente o alerta de sucesso da assinatura eletrônica"""
        try:
            print("⏳ Aguardando confirmação...")
            
            wait = WebDriverWait(self.driver, TIMEOUT_ALERTA_SUCESSO)
            
            # Tentar detectar alerta de sucesso
            try:
                alerta = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="mensagem_descricao_0"]'))
                )
                if "ms7001" in alerta.text.lower() and "evento recebido com sucesso" in alerta.text.lower():
                    print("✅ Assinatura concluída!")
                    return True
                    
            except:
                try:
                    alerta = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'app-reinf-mensagens-alerta .message.success'))
                    )
                    if alerta.is_displayed():
                        texto_alerta = alerta.text
                        if "ms7001" in texto_alerta.lower() and "evento recebido com sucesso" in texto_alerta.lower():
                            print("✅ Assinatura concluída!")
                            return True
                        
                except:
                    try:
                        alerta = wait.until(
                            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'MS7001 - Evento recebido com sucesso')]"))
                        )
                        if alerta.is_displayed():
                            print("✅ Assinatura concluída!")
                            return True
                        
                    except:
                        componente_mensagem = wait.until(
                            EC.presence_of_element_located((By.TAG_NAME, "app-reinf-mensagens-alerta"))
                        )
                        if componente_mensagem.is_displayed():
                            texto_componente = componente_mensagem.text
                            if "sucesso" in texto_componente.lower() and "ms7001" in texto_componente.lower():
                                print("✅ Assinatura concluída!")
                                return True
            
            return False
            
        except Exception as e:
            print("⚠️ Confirmação não detectada - continuando...")
            return False
    
    def realizar_assinatura_automatica(self, metodo_assinatura=1):
        """
        Realiza assinatura eletrônica automaticamente usando PyAutoGUI.
        
        Este método é o core da automação de assinatura, aguardando o aplicativo
        de assinatura (como Assinador Serpro) se estabilizar e executando a
        sequência de comandos apropriada.
        
        Fluxo:
        1. Aguarda 15s para aplicativo de assinatura carregar
        2. Executa método de assinatura selecionado:
           - Método A: Seta ↑, Seta ↑, Enter (recomendado)
           - Método B: Click nas coordenadas + Enter
        3. Retorna sucesso/falha da operação
        
        Args:
            metodo_assinatura (int): Método a usar (1=teclas, 2=mouse)
        
        Returns:
            bool: True se assinatura foi executada com sucesso, False caso contrário
        
        Raises:
            Exception: Capturada e logada, retorna False em caso de erro
        """
        try:
            print("🔐 Executando assinatura automática...")
            
            # Aguardar aplicativo de assinatura
            if not self._aguardar_tempo_fixo(TEMPO_ESPERA_ASSINADOR):
                print("❌ Erro durante espera")
                return False
            
            if metodo_assinatura == 1:
                return self._assinatura_metodo_a()
            elif metodo_assinatura == 2:
                return self._assinatura_metodo_b()
            else:
                print("❌ Método de assinatura inválido")
                return False
                
        except Exception as e:
            print(f"❌ Erro na assinatura automática: {e}")
            return False
    
    def _aguardar_tempo_fixo(self, tempo_espera=15):
        """
        Aguarda um tempo fixo para o aplicativo de assinatura se estabilizar
        
        Args:
            tempo_espera (int): Tempo em segundos para aguardar
        """
        try:
            print(f"⏳ Aguardando {tempo_espera}s...")
            time.sleep(tempo_espera)
            return True
            
        except Exception as e:
            return True  # Continuar mesmo com erro
    
    def _assinatura_metodo_a(self):
        """Método A de assinatura - 3 teclas: Seta ↑, Seta ↑, Enter"""
        try:
            print("⌨️ Método A: ↑ ↑ Enter")
            
            pyautogui.press('up')
            time.sleep(ASSINATURA_METODO_A_INTERVALO)
            pyautogui.press('up')
            time.sleep(ASSINATURA_METODO_A_INTERVALO)
            pyautogui.press('enter')
            time.sleep(TEMPO_ESPERA_CLIQUE)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no Método A: {e}")
            return False
    
    def _assinatura_metodo_b(self):
        """Método B de assinatura - Click do mouse + Enter"""
        try:
            if not self.coordenadas_mouse_metodo_b:
                print("❌ Coordenadas não configuradas")
                return False
            
            x, y = self.coordenadas_mouse_metodo_b
            print(f"🖱️ Método B: Click ({x},{y}) + Enter")
            
            pyautogui.click(x, y)
            time.sleep(ASSINATURA_METODO_B_INTERVALO)
            pyautogui.press('enter')
            time.sleep(TEMPO_ESPERA_CLIQUE)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no Método B: {e}")
            return False
    
    def configurar_coordenadas_metodo_b(self):
        """Configura coordenadas do mouse para Método B de forma interativa"""
        try:
            print("\n🎯 CONFIGURAÇÃO DE COORDENADAS - MÉTODO B")
            print("="*50)
            print("Para o Método B, você precisa definir onde clicar na tela.")
            print("Opções disponíveis:")
            print("1️⃣ - Detectar posição atual do mouse")
            print("2️⃣ - Inserir coordenadas manualmente") 
            print("3️⃣ - Usar coordenadas salvas anteriormente")
            
            opcao = input("\nEscolha uma opção (1, 2 ou 3): ").strip()
            
            if opcao == "1":
                return self._detectar_posicao_mouse()
            elif opcao == "2":
                return self._inserir_coordenadas_manual()
            elif opcao == "3":
                return self._usar_coordenadas_salvas()
            else:
                print("❌ Opção inválida! Digite apenas 1, 2 ou 3")
                print("💡 Tente novamente com uma opção válida")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar coordenadas: {e}")
            return False
    
    def _detectar_posicao_mouse(self):
        """Verifica se há janelas modais ou popups abertos"""
        try:
            # Verificar modais comuns
            modal_selectors = [
                '.modal',
                '.popup',
                '.dialog',
                '[role="dialog"]',
                '[class*="modal"]',
                '[class*="popup"]',
                '.ui-dialog'
            ]
            
            for selector in modal_selectors:
                try:
                    elementos = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elementos:
                        for elemento in elementos:
                            if elemento.is_displayed():
                                print(f"🪟 Modal detectado: {selector}")
                                return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar janelas modais: {e}")
            return False
    
    def _verificar_foco_navegador(self):
        """Verifica se o navegador está em foco e tenta colocá-lo em foco se necessário"""
        try:
            print("🎯 Verificando foco do navegador...")
            
            # Tentar colocar o navegador em foco clicando nele
            try:
                # Pegar o título da janela atual do driver
                titulo_janela = self.driver.title
                print(f"📋 Título da janela: {titulo_janela}")
                
                # Maximizar a janela para garantir que esteja visível
                self.driver.maximize_window()
                
                # Dar foco à janela do navegador
                self.driver.switch_to.window(self.driver.current_window_handle)
                
                print("✅ Foco do navegador verificado e ajustado")
                return True
                
            except Exception as e:
                print(f"⚠️ Erro ao ajustar foco do navegador: {e}")
                print("💡 Continuando sem ajuste de foco...")
                return True
                
        except Exception as e:
            print(f"❌ Erro na verificação de foco: {e}")
            return True  # Continuar mesmo com erro
    
    def _assinatura_metodo_a(self):
        """Método A de assinatura - 3 teclas: Seta ↑, Seta ↑, Enter"""
        try:
            print("🔐 Executando Método A de assinatura...")
            print("📝 Sequência: Seta ↑ → Seta ↑ → Enter")
            
            # A página já foi verificada, pode executar diretamente
            
            # Sequência específica do Método A
            print("1️⃣ Pressionando Seta para Cima...")
            pyautogui.press('up')
            time.sleep(TESTE_METODO_A_INTERVALO)
            
            print("2️⃣ Pressionando Seta para Cima...")
            pyautogui.press('up')
            time.sleep(TESTE_METODO_A_INTERVALO)
            
            print("3️⃣ Pressionando Enter...")
            pyautogui.press('enter')
            time.sleep(TESTE_METODO_B_INTERVALO_FINAL)
            
            print("✅ Método A concluído - sequência de teclas executada")
            return True
            
        except Exception as e:
            print(f"❌ Erro no Método A: {e}")
            return False
    
    def _assinatura_metodo_b(self):
        """Método B de assinatura - Click do mouse + Enter"""
        try:
            print("🔐 Executando Método B de assinatura...")
            print("📝 Sequência: Click do Mouse → Enter")
            
            # Verificar se coordenadas foram configuradas
            if not self.coordenadas_mouse_metodo_b:
                print("❌ Coordenadas do mouse não configuradas para Método B")
                print("💡 Configure as coordenadas antes de executar")
                return False
            
            x, y = self.coordenadas_mouse_metodo_b
            print(f"🎯 Coordenadas configuradas: ({x}, {y})")
            
            # A página já foi verificada, pode executar diretamente
            
            # Sequência específica do Método B
            print("1️⃣ Clicando do mouse na posição configurada...")
            pyautogui.click(x, y)
            time.sleep(TESTE_METODO_B_INTERVALO_CLICK)
            
            print("2️⃣ Pressionando Enter...")
            pyautogui.press('enter')
            time.sleep(TESTE_METODO_B_INTERVALO_FINAL)
            
            print("✅ Método B concluído - click do mouse + Enter executados")
            return True
            
        except Exception as e:
            print(f"❌ Erro no Método B: {e}")
            return False
    
    def configurar_coordenadas_metodo_b(self):
        """Configura coordenadas do mouse para Método B de forma interativa"""
        try:
            print("\n🎯 CONFIGURAÇÃO DE COORDENADAS - MÉTODO B")
            print("="*50)
            print("Para o Método B, você precisa definir onde clicar na tela.")
            print("Opções disponíveis:")
            print("1️⃣ - Detectar posição atual do mouse")
            print("2️⃣ - Inserir coordenadas manualmente") 
            print("3️⃣ - Usar coordenadas salvas anteriormente")
            
            opcao = input("\nEscolha uma opção (1, 2 ou 3): ").strip()
            
            if opcao == "1":
                return self._detectar_posicao_mouse()
            elif opcao == "2":
                return self._inserir_coordenadas_manual()
            elif opcao == "3":
                return self._usar_coordenadas_salvas()
            else:
                print("❌ Opção inválida! Digite apenas 1, 2 ou 3")
                print("💡 Tente novamente com uma opção válida")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar coordenadas: {e}")
            return False
    
    def _detectar_posicao_mouse(self):
        """Detecta a posição atual do mouse para usar como coordenadas"""
        try:
            print("\n🖱️ DETECÇÃO DE POSIÇÃO DO MOUSE")
            print("="*40)
            print("1. Posicione o mouse EXATAMENTE onde deve clicar")
            print("2. Pressione ENTER quando estiver na posição correta")
            print("3. ⚠️ NÃO mova o mouse após pressionar ENTER!")
            
            input("\nPositione o mouse e pressione ENTER...")
            
            # Capturar posição atual
            x, y = pyautogui.position()
            coordenadas = (x, y)
            self.coordenadas_mouse_metodo_b = coordenadas
            
            # Salvar no config.py
            self.salvar_coordenadas_config(coordenadas)
            
            print(f"✅ Coordenadas capturadas: ({x}, {y})")
            print("💾 Coordenadas salvas para o Método B")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao detectar posição: {e}")
            return False
    
    def _inserir_coordenadas_manual(self):
        """Permite inserir coordenadas manualmente"""
        try:
            print(f"\n⌨️ INSERÇÃO MANUAL DE COORDENADAS")
            print("="*40)
            print(f"📏 Resolução da sua tela: {pyautogui.size()}")
            
            while True:
                try:
                    x = int(input("Digite a coordenada X (horizontal): "))
                    y = int(input("Digite a coordenada Y (vertical): "))
                    
                    # Validar coordenadas
                    largura, altura = pyautogui.size()
                    if 0 <= x <= largura and 0 <= y <= altura:
                        coordenadas = (x, y)
                        self.coordenadas_mouse_metodo_b = coordenadas
                        
                        # Salvar no config.py
                        self.salvar_coordenadas_config(coordenadas)
                        
                        print(f"✅ Coordenadas definidas: ({x}, {y})")
                        return True
                    else:
                        print(f"❌ Coordenadas inválidas! Use: X (0-{largura}), Y (0-{altura})")
                        
                except ValueError:
                    print("❌ Digite apenas números inteiros")
                    
        except Exception as e:
            print(f"❌ Erro ao inserir coordenadas: {e}")
            return False
    
    def _usar_coordenadas_salvas(self):
        """Usa coordenadas previamente salvas do config.py"""
        # Recarregar coordenadas do config.py para pegar valores atualizados
        try:
            from config import COORDENADAS_MOUSE_METODO_B
            self.coordenadas_mouse_metodo_b = COORDENADAS_MOUSE_METODO_B
        except ImportError:
            pass
        
        if self.coordenadas_mouse_metodo_b:
            x, y = self.coordenadas_mouse_metodo_b
            print(f"✅ Usando coordenadas salvas do config.py: ({x}, {y})")
            return True
        else:
            print("❌ Nenhuma coordenada salva encontrada no config.py")
            print("💡 Você precisa configurar as coordenadas primeiro")
            print("💡 Escolha opção 1 (detectar posição) ou 2 (inserir manual)")
            return False
    
    def detectar_elementos_tela(self):
        """Detecta elementos na tela para auxiliar na assinatura"""
        try:
            print("🔍 Detectando elementos na tela...")
            
            # Obter tamanho da tela
            largura_tela, altura_tela = pyautogui.size()
            print(f"📏 Resolução da tela: {largura_tela}x{altura_tela}")
            
            # Capturar screenshot da tela atual
            screenshot = pyautogui.screenshot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_screenshot = f"screenshot_assinatura_{timestamp}.png"
            screenshot.save(nome_screenshot)
            print(f"📸 Screenshot salvo: {nome_screenshot}")
            
            return {
                'largura': largura_tela,
                'altura': altura_tela,
                'screenshot': nome_screenshot
            }
            
        except Exception as e:
            print(f"❌ Erro ao detectar elementos: {e}")
            return None
    
    def clicar_proximo_cpf(self):
        """Clica no botão 'Incluir novo pagamento' para ir ao próximo CPF"""
        try:
            print("➡️ Próximo CPF...")
            time.sleep(TEMPO_ANTES_PROXIMO_CPF)
            wait = WebDriverWait(self.driver, TIMEOUT_PROXIMO_CPF)
            
            try:
                # Método 1: Tentar localizar pelo texto exato
                botao_proximo = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Incluir novo pagamento')]"))
                )
                print("✅ Botão encontrado pelo texto")
            except:
                try:
                    # Método 2: Tentar localizar pela classe + texto
                    print("⚠️ Tentando localizar pela classe e texto...")
                    botao_proximo = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@class='button' and contains(text(), 'Incluir novo pagamento')]"))
                    )
                    print("✅ Botão encontrado pela classe + texto")
                except:
                    # Método 3: Tentar localizar apenas pela classe e verificar texto
                    print("⚠️ Tentando localizar apenas pela classe...")
                    botoes = self.driver.find_elements(By.CSS_SELECTOR, "button.button")
                    botao_proximo = None
                    
                    for botao in botoes:
                        if "incluir novo pagamento" in botao.text.lower():
                            botao_proximo = botao
                            break
                    
                    if botao_proximo:
                        print("✅ Botão encontrado pela classe com verificação de texto")
                    else:
                        raise Exception("Botão não encontrado por nenhum método")
            
            # Scroll até o botão para garantir visibilidade
            print("📜 Fazendo scroll até o botão...")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", botao_proximo)
            time.sleep(TEMPO_APOS_SCROLL)
            
            # Clicar no botão
            print("🖱️ Clicando no botão 'Incluir novo pagamento'...")
            botao_proximo.click()
            
            print("✅ Botão 'Incluir novo pagamento' clicado com sucesso!")
            print("⏳ Aguardando redirecionamento para próximo formulário...")
            
            # Aguardar a próxima página carregar
            time.sleep(TEMPO_APOS_PROXIMO_CPF)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao clicar no botão próximo CPF: {e}")
            print("💡 Verifique se a assinatura eletrônica foi completada corretamente")
            print("💡 O botão 'Incluir novo pagamento' pode demorar alguns segundos para aparecer")
            return False
    
    def preencher_formulario(self, cpf_titular):
        """Preenche o formulário automaticamente"""
        print("\n" + "="*60)
        print("🤖 INICIANDO PREENCHIMENTO AUTOMÁTICO")
        print("="*60)
        
        # ETAPA 1: Preencher dados iniciais
        if not self.preencher_dados_iniciais(cpf_titular):
            print("❌ Falha no preenchimento inicial")
            return False
        
        # ETAPA 2: Continuar para próxima etapa
        if not self.continuar_para_proxima_etapa():
            print("❌ Falha ao continuar para próxima etapa")
            return False
        
        # ETAPA 3: Aguardar instruções para próximos elementos
        print("\n✅ Primeira etapa concluída!")
        print("\n⏸️ Aguardando próximas instruções...")
        print("Me diga o que aparece na tela DEPOIS de clicar em 'Continuar'!")
        
        return True
    
    def carregar_dados(self):
        """Carrega dados do Excel"""
        print("\n📂 Carregando dados do Excel...")
        try:
            dados = pd.read_excel(ARQUIVO_EXCEL, sheet_name=PLANILHA, skiprows=1)
            dados_limpos = dados.dropna(how='all')
            dados_limpos = dados_limpos[dados_limpos['CPF'].notna()]
            
            # Pegar primeiro titular
            titular = dados_limpos[dados_limpos['DEPENDENCIA'] == 'Titular'].iloc[0]
            
            print(f"✅ Dados carregados!")
            print(f"\n👤 TITULAR: {titular['NOME']}")
            print(f"   CPF: {titular['CPF']}")
            
            return titular['CPF']
        except Exception as e:
            print(f"❌ Erro ao carregar Excel: {e}")
            return None
    
    def processar_dataframe_por_grupos(self):
        """Processa o dataframe agrupando por titular"""
        try:
            print("\n📊 Processando dados do Excel por grupos...")
            dados = pd.read_excel(ARQUIVO_EXCEL, sheet_name=PLANILHA, skiprows=1)
            dados_limpos = dados.dropna(how='all')
            dados_limpos = dados_limpos[dados_limpos['CPF'].notna()]
            
            # Agrupar por titular
            grupos = []
            grupo_atual = []
            
            for index, row in dados_limpos.iterrows():
                if pd.isna(row['NOME']) or str(row['NOME']).strip() == '':
                    continue
                if pd.isna(row['DEPENDENCIA']) or str(row['DEPENDENCIA']).strip() == '':
                    continue
                if pd.isna(row['CPF']) or str(row['CPF']).strip() == '':
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
            
            print(f"✅ {len(grupos)} grupos (titulares) encontrados")
            return grupos
            
        except Exception as e:
            print(f"❌ Erro ao processar dataframe: {e}")
            return []
    
    def salvar_checkpoint_indice(self, indice_grupo):
        """Salva o checkpoint do último grupo processado"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            # Criar tabela de checkpoint de índice se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkpoint_indice (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ultimo_indice INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Inserir ou atualizar checkpoint
            cursor.execute('DELETE FROM checkpoint_indice')
            cursor.execute('INSERT INTO checkpoint_indice (ultimo_indice) VALUES (?)', (indice_grupo,))
            
            conn.commit()
            conn.close()
            print(f"💾 Checkpoint de índice salvo: grupo {indice_grupo}")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar checkpoint de índice: {e}")
    
    def carregar_checkpoint_indice(self):
        """Carrega o checkpoint do último grupo processado"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            cursor.execute('SELECT ultimo_indice FROM checkpoint_indice ORDER BY timestamp DESC LIMIT 1')
            resultado = cursor.fetchone()
            
            conn.close()
            
            if resultado:
                indice = resultado[0]
                print(f"📂 Checkpoint de índice encontrado: grupo {indice}")
                return indice
            else:
                print("📂 Nenhum checkpoint de índice encontrado")
                return -1
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar checkpoint de índice: {e}")
            return -1
    
    def processar_todos_os_grupos(self):
        """Processa todos os grupos, pulando automaticamente em caso de erro"""
        try:
            print("\n" + "="*60)
            print("🤖 PROCESSANDO TODOS OS GRUPOS")
            print("="*60)
            
            # Carregar grupos
            grupos = self.processar_dataframe_por_grupos()
            if not grupos:
                print("❌ Nenhum grupo encontrado")
                return
            
            print(f"📊 Total de grupos: {len(grupos)}")
            
            # Verificar checkpoint de índice
            checkpoint_indice = self.carregar_checkpoint_indice()
            inicio = 0
            
            if checkpoint_indice >= 0:
                print(f"🔄 Checkpoint encontrado no grupo {checkpoint_indice + 1}")
                print("💡 Continuando de onde parou...")
                inicio = checkpoint_indice + 1
            
            # Verificar se já terminou
            if inicio >= len(grupos):
                print("✅ Todos os grupos já foram processados!")
                return
            
            print(f"📊 Processando grupos {inicio + 1} até {len(grupos)}")
            
            sucessos = 0
            erros = 0
            pulados = 0
            
            for i in range(inicio, len(grupos)):
                grupo = grupos[i]
                print(f"\n{'='*60}")
                print(f"🔄 Processando grupo {i+1}/{len(grupos)}")
                
                titular = grupo[0]  # Primeiro item é sempre o titular
                dependentes = grupo[1:] if len(grupo) > 1 else []
                
                print(f"👤 Titular: {titular['NOME']} - CPF: {titular['CPF']}")
                print(f"👥 Dependentes: {len(dependentes)}")
                
                # Verificar se grupo já foi completamente processado ANTES de tentar processar
                cpf_titular = titular['CPF'] 
                if self.verificar_grupo_completamente_processado(cpf_titular):
                    print(f"✅ Grupo {cpf_titular} já foi completamente processado - pulando")
                    sucessos += 1
                    continue
                
                # Verificar se grupo foi pulado (ex: CPF já lançado)
                if self.verificar_ultimo_status_pulado(cpf_titular):
                    print(f"⏭️ Grupo {cpf_titular} foi pulado anteriormente - pulando")
                    sucessos += 1
                    continue
                
                # Tentar processar este grupo
                try:
                    resultado = self.processar_grupo_individual(titular, dependentes)
                    
                    if resultado == "sucesso":
                        sucessos += 1
                        print(f"✅ Grupo {i+1} processado com sucesso!")
                        # Salvar checkpoint após sucesso
                        self.salvar_checkpoint_indice(i)
                    elif resultado == "pulado":
                        pulados += 1
                        print(f"⏭️ Grupo {i+1} pulado (CPF já lançado)")
                        # Salvar checkpoint mesmo quando pulado
                        self.salvar_checkpoint_indice(i)
                    else:
                        erros += 1
                        print(f"❌ Grupo {i+1} falhou")
                        
                        # Salvar checkpoint com status "erro" na tabela progresso_efd
                        cpf_titular = titular['CPF']
                        nome_titular = titular['NOME']
                        self.salvar_checkpoint(
                            cpf_titular,
                            nome_titular,
                            "grupo_erro",
                            "erro",
                            observacoes=f"Grupo falhou durante processamento"
                        )
                        
                        # Salvar checkpoint do grupo atual para reprocessar
                        self.salvar_checkpoint_indice(i)
                        
                except Exception as e:
                    # Capturar erros não tratados (ex: erros do Chrome/Selenium)
                    erros += 1
                    print(f"❌ Erro não tratado ao processar grupo {i+1}: {e}")
                    traceback.print_exc()
                    
                    # Salvar checkpoint com status "erro"
                    cpf_titular = titular['CPF']
                    nome_titular = titular['NOME']
                    self.salvar_checkpoint(
                        cpf_titular,
                        nome_titular,
                        "grupo_erro",
                        "erro",
                        observacoes=f"Erro não tratado durante processamento: {str(e)}"
                    )
                    
                    # Salvar checkpoint do grupo atual para reprocessar
                    self.salvar_checkpoint_indice(i)
                
                # Pequena pausa entre grupos
                time.sleep(TEMPO_ENTRE_GRUPOS)
            
            # Resumo final
            print(f"\n{'='*60}")
            print("📊 RESUMO FINAL")
            print(f"{'='*60}")
            print(f"Total de grupos: {len(grupos)}")
            print(f"✅ Sucessos: {sucessos}")
            print(f"⏭️ Pulados: {pulados}")
            print(f"❌ Erros: {erros}")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"❌ Erro ao processar grupos: {e}")
    
    def processar_grupo_individual(self, titular, dependentes):
        """
        Processa um grupo completo (titular + dependentes) com automação total.
        
        Esta função gerencia o processo completo de um CPF, incluindo:
        1. Preenchimento automático dos dados do titular
        2. Adição de todos os dependentes e planos
        3. Envio automático da declaração
        4. Assinatura eletrônica automatizada
        5. Detecção de confirmação de sucesso
        6. Navegação para próximo CPF
        7. Salvamento de checkpoints em cada etapa
        
        Args:
            titular (pandas.Series): Dados do titular (primeira linha do grupo)
            dependentes (pandas.DataFrame): DataFrame com todos os dependentes do grupo
        
        Returns:
            bool: True se grupo foi processado com sucesso, False em caso de erro
        
        O método implementa verificação manual opcional e tratamento robusto de erros,
        salvando checkpoints detalhados para permitir retomada em caso de falha.
        
        Checkpoints salvos:
        - dados_preenchidos: Após preencher formulário
        - declaracao_enviada: Após envio bem-sucedido
        - assinatura_completa: Após assinatura confirmada
        - grupo_completo: Após assinatura confirmada
        - erro_*: Em caso de falhas específicas
        """
        try:
            cpf_titular = titular['CPF']
            nome_titular = titular['NOME']
            
            # Verificar se o valor do titular é zero ou nulo - se for, pular o grupo inteiro
            valor_titular_raw = titular.get('VALOR_PLANO') or titular.get('TOTAL')
            
            # Se não houver valor, considerar como nulo (pular grupo)
            if valor_titular_raw is None or self.valor_eh_zero_ou_nulo(valor_titular_raw):
                print(f"\n{'='*60}")
                print(f"⏭️ GRUPO PULADO - VALOR DO TITULAR É ZERO OU NULO")
                print(f"{'='*60}")
                print(f"👤 Titular: {nome_titular} - CPF: {cpf_titular}")
                print(f"💰 Valor do plano: {valor_titular_raw if valor_titular_raw is not None else 'N/A'}")
                print(f"ℹ️ Grupo inteiro será pulado (titular não assina mais o plano ou valor não informado)")
                
                # Salvar checkpoint com status "pulado"
                self.salvar_checkpoint(
                    cpf_titular,
                    nome_titular,
                    "grupo_pulado",
                    "pulado",
                    observacoes=f"Grupo pulado - valor do titular é zero ou nulo (não assina mais o plano)"
                )
                
                return "pulado"
            
            # Se há dados parciais (grupo incompleto), limpar tudo
            print(f"🔍 Verificando dados parciais para {cpf_titular}...")
            
            # Verificar se há dependentes ou planos salvos (dados parciais)
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM dependentes_processados WHERE cpf_titular = ?', (cpf_titular,))
            dependentes_parciais = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM planos_processados WHERE cpf_titular = ?', (cpf_titular,))
            planos_parciais = cursor.fetchone()[0]
            
            conn.close()
            
            if dependentes_parciais > 0 or planos_parciais > 0:
                print(f"🧹 Encontrados dados parciais para {cpf_titular} - limpando para recomeçar...")
                self.limpar_dados_parciais_grupo(cpf_titular)
            
            # Preencher dados iniciais
            if not self.preencher_dados_iniciais(cpf_titular, nome_titular):
                print(f"❌ Falha no preenchimento inicial para {cpf_titular}")
                self.limpar_dados_parciais_grupo(cpf_titular)
                return "erro"
            
            # Continuar para próxima etapa
            if not self.continuar_para_proxima_etapa():
                print(f"❌ Falha ao continuar para próxima etapa para {cpf_titular}")
                
                # Verificar se foi erro de "CPF já lançado" (status pulado)
                if self.verificar_ultimo_status_pulado(cpf_titular):
                    print(f"⏭️ CPF {cpf_titular} foi pulado (já lançado) - mantendo dados salvos")
                    return "pulado"
                else:
                    # Erro real - limpar dados parciais
                    self.limpar_dados_parciais_grupo(cpf_titular)
                    return "erro"
            
            # Processar dependentes
            self.processar_dependentes_grupo(dependentes)
            
            # Processar planos de saúde
            self.processar_planos_grupo(titular)
            
            # Processar informações dos dependentes (valores pagos pelos dependentes)
            self.processar_info_dependentes_grupo(dependentes)
            
            # VERIFICAÇÃO CONDICIONAL DOS DADOS
            if self.verificar_dados_manual:
                # PAUSA PARA ANÁLISE - Verificar se tudo está correto
                print(f"\n{'='*60}")
                print("⏸️ PAUSA PARA ANÁLISE")
                print(f"{'='*60}")
                print("📋 Verifique se todos os dados foram preenchidos corretamente:")
                print("   ✅ Dados iniciais (Período, CNPJ, CPF)")
                print("   ✅ Dependentes (se houver)")
                print("   ✅ Planos de saúde (se houver)")
                print("   ✅ Informações dos dependentes (se houver)")
                print("\n💡 Após verificar, pressione ENTER para continuar...")
                print("   (Ou Ctrl+C para interromper)")
                
                try:
                    input("\n⏸️ Pressione ENTER para continuar ou Ctrl+C para interromper...")
                except (EOFError, KeyboardInterrupt):
                    print(f"\n⚠️ Executando via script - aguardando {TEMPO_SCRIPT_VERIFICACAO}s...")
                    time.sleep(TEMPO_SCRIPT_VERIFICACAO)
            else:
                # Modo automático - sem verificação manual
                print(f"\n{'='*60}")
                print("🚀 MODO AUTOMÁTICO ATIVADO")
                print(f"{'='*60}")
                print("⚡ Prosseguindo automaticamente para envio da declaração...")
                print("   ✅ Dados iniciais processados")
                print("   ✅ Dependentes processados (se houver)")
                print("   ✅ Planos de saúde processados (se houver)")
                print("   ✅ Informações dos dependentes processadas (se houver)")
                print(f"\n⏳ Aguardando {TEMPO_MODO_AUTOMATICO}s antes do envio...")
                time.sleep(TEMPO_MODO_AUTOMATICO)
            
            # ETAPA FINAL: Enviar declaração
            print(f"\n{'='*60}")
            print("📤 ENVIANDO DECLARAÇÃO")
            print(f"{'='*60}")
            
            if self.enviar_declaracao():
                print("✅ Declaração enviada com sucesso!")
                
                # Executar assinatura eletrônica automática
                assinatura_sucesso = self.realizar_assinatura_automatica(self.metodo_assinatura)
                
                if assinatura_sucesso:
                    # Aguardar automaticamente pelo alerta de sucesso
                    if self.aguardar_alerta_sucesso_assinatura():
                        print("✅ Processo concluído!")
                        
                        # GRUPO COMPLETO! Salvar checkpoint final imediatamente após assinatura
                        self.salvar_checkpoint(
                            cpf_titular,
                            nome_titular,
                            "grupo_completo",
                            "sucesso",
                            observacoes="Grupo processado completamente - assinatura concluída com sucesso"
                        )
                        
                    else:
                        print("⚠️ Confirmação não detectada - continuando...")
                        time.sleep(TEMPO_CONFIRMACAO_NAO_DETECTADA)
                        
                        # Mesmo sem confirmação detectada, consideramos grupo completo se chegou até aqui
                        self.salvar_checkpoint(
                            cpf_titular,
                            nome_titular,
                            "grupo_completo",
                            "sucesso",
                            observacoes="Grupo processado completamente - confirmação não detectada mas assinatura executada"
                        )
                        
                else:
                    print("❌ Erro na assinatura")
                    time.sleep(TEMPO_ERRO_ASSINATURA)
                
                # Salvar checkpoint com assinatura completa (para histórico)
                self.salvar_checkpoint(
                    cpf_titular,
                    nome_titular,
                    "assinatura_completa",
                    "sucesso",
                    observacoes="Declaração enviada e assinatura eletrônica executada"
                )
                
                # Próximo passo: clicar no botão próximo CPF
                print(f"\n{'='*60}")
                print("➡️ PRÓXIMO CPF")
                print(f"{'='*60}")
                
                if self.clicar_proximo_cpf():
                    print("✅ Botão próximo CPF clicado com sucesso!")
                    return "sucesso"
                else:
                    print("❌ Erro ao clicar no botão próximo CPF")
                    
                    # Salvar checkpoint com erro no próximo CPF
                    self.salvar_checkpoint(
                        cpf_titular,
                        nome_titular,
                        "erro_proximo_cpf",
                        "erro",
                        observacoes="Erro ao clicar no botão próximo CPF - verificar manualmente"
                    )
                    
                    self.limpar_dados_parciais_grupo(cpf_titular)
                    return "erro"
            else:
                print("❌ Falha ao enviar declaração")
                
                # Salvar checkpoint com erro no envio
                self.salvar_checkpoint(
                    cpf_titular,
                    nome_titular,
                    "erro_envio",
                    "erro",
                    observacoes="Erro ao enviar declaração - verificar manualmente"
                )
                
                self.limpar_dados_parciais_grupo(cpf_titular)
                return "erro"
            
        except Exception as e:
            print(f"❌ Erro ao processar grupo individual: {e}")
            traceback.print_exc()
            
            # Salvar checkpoint com status "erro"
            self.salvar_checkpoint(
                cpf_titular,
                nome_titular,
                "erro_processamento",
                "erro",
                observacoes=f"Erro durante processamento: {str(e)}"
            )
            
            self.limpar_dados_parciais_grupo(cpf_titular)
            return "erro"
    
    def processar_dependentes_grupo(self, dependentes):
        """Processa todos os dependentes de um grupo"""
        try:
            if not dependentes:
                print("ℹ️ Nenhum dependente para processar")
                return
            
            print(f"\n👥 Processando {len(dependentes)} dependentes...")
            
            dependentes_pulados = 0
            
            for dependente in dependentes:
                cpf_dep = dependente['CPF']
                
                # Verificar se o valor do dependente é nulo ANTES de adicionar à lista
                valor_dependente_raw = dependente.get('VALOR_DEPENDENTE') or dependente.get('TOTAL')
                if valor_dependente_raw is None or self.valor_eh_zero_ou_nulo(valor_dependente_raw):
                    print(f"   ⏭️ Dependente {cpf_dep} tem valor zero ou nulo - não será adicionado (não assina mais o plano)")
                    dependentes_pulados += 1
                    continue
                
                dependencia_original = dependente.get('DEPENDENCIA', '').strip()
                
                # Mapear dependência para valor do formulário
                relacao_valor = self.mapear_dependencia(dependencia_original)
                agregado_outros = None
                
                # Se for "Agregado/Outros", usar a dependência original como especificação
                if relacao_valor == '99':  # 99 = "Agregado/Outros"
                    agregado_outros = dependencia_original
                
                print(f"   📝 Adicionando dependente: {cpf_dep}")
                print(f"      Relação: {dependencia_original} → {relacao_valor}")
                if agregado_outros:
                    print(f"      Descrição: {agregado_outros}")
                
                
                # Verificar se dependente já foi processado
                if self.verificar_dependente_processado(self.cpf_titular_atual, cpf_dep):
                    print(f"   ⚠️ Dependente {cpf_dep} já foi processado - pulando")
                    continue
                
                # Adicionar dependente
                if self.adicionar_dependente(cpf_dep, relacao_valor, agregado_outros):
                    print(f"   ✅ Dependente {cpf_dep} adicionado com sucesso")
                else:
                    print(f"   ❌ Falha ao adicionar dependente {cpf_dep}")
            
            if dependentes_pulados > 0:
                print(f"\n   ℹ️ Total de dependentes não adicionados (valor zero/nulo): {dependentes_pulados}")
        
        except Exception as e:
            print(f"❌ Erro ao processar dependentes: {e}")
    
    def processar_planos_grupo(self, titular):
        """Processa planos de saúde de um grupo"""
        try:
            # Dados do plano - usando dados do Excel
            cnpj_operadora = titular.get('CNPJ_OPERADORA', CNPJ_OPERADORA_PADRAO)  # CNPJ padrão
            valor_titular_raw = titular.get('VALOR_PLANO', titular.get('TOTAL', "100.00"))  # Valor do Excel
            valor_titular = self.formatar_valor(valor_titular_raw)  # Formatar com 2 casas decimais
            
            print(f"\n🏥 Processando plano de saúde...")
            print(f"   CNPJ: {cnpj_operadora}")
            print(f"   Valor: {valor_titular}")
            
            
            # Verificar se plano já foi processado
            if self.verificar_plano_processado(self.cpf_titular_atual, cnpj_operadora):
                print(f"   ⚠️ Plano já foi processado - pulando")
                return
            
            # Adicionar plano
            if self.adicionar_plano_saude(cnpj_operadora, valor_titular):
                print(f"   ✅ Plano adicionado com sucesso")
            else:
                print(f"   ❌ Falha ao adicionar plano")
        
        except Exception as e:
            print(f"❌ Erro ao processar planos: {e}")
    
    def processar_info_dependentes_grupo(self, dependentes):
        """Processa informações dos dependentes (valores pagos pelos dependentes)"""
        try:
            if not dependentes:
                print("ℹ️ Nenhum dependente para processar informações")
                return
            
            print(f"\n💰 Processando informações de {len(dependentes)} dependentes...")
            
            dependentes_pulados = 0
            
            for dependente in dependentes:
                cpf_dep = dependente['CPF']
                valor_dependente_raw = dependente.get('VALOR_DEPENDENTE', dependente.get('TOTAL', "50.00"))
                
                # Verificar se o valor é zero ou nulo ANTES de processar
                if self.valor_eh_zero_ou_nulo(valor_dependente_raw):
                    print(f"   ⏭️ Dependente {cpf_dep} tem valor zero ou nulo - pulando (não assina mais o plano)")
                    dependentes_pulados += 1
                    continue
                
                valor_dependente = self.formatar_valor(valor_dependente_raw)  # Formatar com 2 casas decimais
                
                print(f"   💰 Adicionando informação do dependente: {cpf_dep}")
                print(f"      Valor: {valor_dependente}")
                
                # Verificar se informação já foi processada
                if self.verificar_info_dependente_processado(self.cpf_titular_atual, cpf_dep):
                    print(f"   ⚠️ Informação do dependente {cpf_dep} já foi processada - pulando")
                    continue
                
                # Adicionar informação do dependente
                if self.adicionar_informacao_dependente(cpf_dep, valor_dependente):
                    print(f"   ✅ Informação do dependente {cpf_dep} adicionada com sucesso")
                else:
                    print(f"   ❌ Falha ao adicionar informação do dependente {cpf_dep}")
            
            if dependentes_pulados > 0:
                print(f"\n   ℹ️ Total de dependentes pulados (valor zero/nulo): {dependentes_pulados}")
        
        except Exception as e:
            print(f"❌ Erro ao processar informações dos dependentes: {e}")
    
    def verificar_dependente_processado(self, cpf_titular, cpf_dependente):
        """Verifica se um dependente já foi processado"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM dependentes_processados 
                WHERE cpf_titular = ? AND cpf_dependente = ?
            ''', (cpf_titular, cpf_dependente))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except:
            return False
    
    def verificar_plano_processado(self, cpf_titular, cnpj_operadora):
        """Verifica se um plano já foi processado"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM planos_processados 
                WHERE cpf_titular = ? AND cnpj_operadora = ?
            ''', (cpf_titular, cnpj_operadora))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except:
            return False
    
    def verificar_info_dependente_processado(self, cpf_titular, cpf_dependente):
        """Verifica se uma informação de dependente já foi processada"""
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM info_dependentes_processados 
                WHERE cpf_titular = ? AND cpf_dependente = ?
            ''', (cpf_titular, cpf_dependente))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except:
            return False
    
    def executar(self):
        """
        Função principal que executa todo o processo de automação EFD-REINF.
        
        Esta é a função de entrada principal que:
        1. Coleta configurações do usuário (verificação manual, método de assinatura)
        2. Configura coordenadas para método B se necessário
        3. Abre o site da Receita Federal
        4. Aguarda login manual do usuário
        5. Processa todos os grupos do Excel automaticamente
        6. Gera relatórios de progresso
        
        Configurações solicitadas:
        - Verificação manual de dados (S/N)
        - Método de assinatura (1=teclas, 2=mouse)
        - Coordenadas do mouse (apenas para método 2)
        
        O processo continua até todos os CPFs serem processados ou erro fatal.
        Checkpoints permitem retomar o processo posteriormente.
        
        Raises:
            Exception: Capturadas e logadas, processo pode ser retomado via checkpoints
        """
        print("\n" + "="*60)
        print("🤖 AUTOMAÇÃO EFD-REINF")
        print("="*60)
        print("\n💡 FUNCIONAMENTO:")
        print("   1. Chrome abre no site")
        print("   2. VOCÊ faz login e navega até o formulário")
        print("   3. CÓDIGO processa TODOS os grupos automaticamente")
        print("   4. Pula automaticamente CPFs já lançados")
        print("   5. ✨ NOVO: Envia automaticamente cada declaração")
        print("="*60)
        
        # Configurações automáticas do config.py
        print("\n⚙️ CONFIGURAÇÕES AUTOMÁTICAS")
        print("="*40)
        
        # Configurar verificação manual usando config.py
        if VERIFICACAO_MANUAL_PADRAO:
            print("✅ Modo MANUAL: Com verificação antes do envio")
            print("💡 O sistema pausará para você verificar os dados")
        else:
            print("✅ Modo AUTOMÁTICO: Sem verificação manual")
            print("⚠️ O sistema enviará as declarações automaticamente!")
        
        # Configurar método de assinatura básico usando config.py
        if METODO_ASSINATURA_PADRAO == 2:
            self.metodo_assinatura = 2
            print("✅ Método B selecionado (sequência alternativa)")
        else:
            self.metodo_assinatura = 1
            print("✅ Método A selecionado (sequência padrão)")
        
        print("\n💡 Para alterar essas configurações, edite o arquivo config.py")
        print("="*60)
        
        # Abrir site
        self.abrir_site()
        
        # Aguardar login e navegação manual
        self.aguardar_login()
        
        # Configurar coordenadas para Método B DEPOIS de acessar o ECAC
        if METODO_ASSINATURA_PADRAO == 2:
            print("\n" + "="*60)
            print("📍 CONFIGURAÇÃO DE COORDENADAS - MÉTODO B")
            print("="*60)
            print("Agora que o ECAC está aberto, configure as coordenadas do mouse")
            print("para o Método B de assinatura eletrônica.")
            
            coordenadas_configuradas = False
            
            while not coordenadas_configuradas:
                try:
                    if self.configurar_coordenadas_metodo_b():
                        coordenadas_configuradas = True
                        print("✅ Coordenadas configuradas com sucesso!")
                    else:
                        print("\n⚠️ Falha na configuração de coordenadas")
                        print("Opções:")
                        print("1️⃣ - Tentar novamente")
                        print("2️⃣ - Mudar para Método A")
                        print("3️⃣ - Cancelar execução")
                        
                        opcao_erro = input("\nEscolha uma opção (1, 2 ou 3): ").strip()
                        
                        if opcao_erro == "1":
                            print("🔄 Tentando configurar coordenadas novamente...")
                            continue
                        elif opcao_erro == "2":
                            print("🔄 Mudando para Método A...")
                            self.metodo_assinatura = 1
                            coordenadas_configuradas = True  # Sair do loop
                        elif opcao_erro == "3":
                            print("❌ Execução cancelada pelo usuário")
                            return  # Sair da função executar
                        else:
                            print("⚠️ Opção inválida, tentando novamente...")
                            continue
                            
                except (EOFError, KeyboardInterrupt):
                    print("\n🔄 Mudando para Método A devido à interrupção...")
                    self.metodo_assinatura = 1
                    coordenadas_configuradas = True
        
        # Processar todos os grupos
        self.processar_todos_os_grupos()
        
        print("\n✅ Processo concluído!")
        print("💡 Use o gerenciador de checkpoint para ver detalhes: python gerenciar_checkpoint.py")
        print("🚀 Sistema totalmente funcional com automação completa!")

# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    """Função principal"""
    automacao = None
    
    try:
        automacao = AutomacaoEFD()
        automacao.executar()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if automacao:
            automacao.fechar()

if __name__ == "__main__":
    main()

