"""
Automação EFD-REINF - Receita Federal
Sistema para automatizar preenchimento de formulários
"""

# Imports
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
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

# Configurar encoding UTF-8 para Windows
if platform.system() == "Windows":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL_BASE = 'https://cav.receita.fazenda.gov.br/ecac/Aplicacao.aspx?id=10019&origem=menu'
ARQUIVO_EXCEL = 'dados.xlsx'
PLANILHA = 'MAR 2025'

# ============================================================
# CLASSE PRINCIPAL
# ============================================================

class AutomacaoEFD:
    """Classe principal para automação do EFD-REINF"""
    
    def __init__(self):
        """Inicializa a automação"""
        self.driver = None
        self.configurar_chrome()
    
    def configurar_chrome(self):
        """Configura e abre o Chrome"""
        print("\n" + "="*60)
        print("🔧 CONFIGURANDO CHROME")
        print("="*60)
        
        print("\n⚠️ IMPORTANTE: Site do governo pode bloquear perfis novos!")
        print("\n📋 OPÇÕES:")
        print("   1. Usar seu PERFIL REAL do Chrome (onde certificado está)")
        print("   2. Usar perfil DEDICADO de automação")
        print("="*60)
        
        escolha = input("\nEscolha (1 ou 2) [recomendado: 1]: ").strip() or "1"
        
        options = uc.ChromeOptions()
        
        if escolha == "1":
            # Usar perfil REAL do Chrome
            print("\n✅ Usando seu perfil REAL do Chrome")
            print("⚠️ FECHE TODAS AS JANELAS DO CHROME antes de continuar!")
            input("Pressione ENTER quando Chrome estiver fechado...")
            
            # Caminho padrão do perfil do Chrome no Windows
            if platform.system() == "Windows":
                user_profile = os.environ.get('USERPROFILE', '')
                chrome_profile = os.path.join(user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
                
                print(f"📂 Perfil: {chrome_profile}")
                options.add_argument(f'--user-data-dir={chrome_profile}')
                options.add_argument('--profile-directory=Default')
        else:
            # Usar perfil DEDICADO
            print("\n✅ Usando perfil dedicado de automação")
            profile_dir = os.path.join(os.getcwd(), "chrome_efd")
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)
                print("📁 Perfil criado")
            
            options.add_argument(f'--user-data-dir={profile_dir}')
        
        options.add_argument('--start-maximized')
        
        print("🚀 Abrindo Chrome...")
        self.driver = uc.Chrome(options=options, use_subprocess=True)
        
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
        input("\n✅ VÊ OS 3 CAMPOS NA TELA? Pressione ENTER para automação...\n")
    
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
        input("\nPressione ENTER para continuar...")
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            print("\n🔒 Fechando Chrome...")
            self.driver.quit()
            print("✅ Chrome fechado!")
    
    # ============================================================
    # FUNÇÕES DE AUTOMAÇÃO (a serem implementadas)
    # ============================================================
    
    def delay_humano(self, min_sec=0.3, max_sec=0.8):
        """Adiciona delay aleatório para simular comportamento humano"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def digitar_devagar(self, elemento, texto):
        """Digita texto caractere por caractere"""
        for char in str(texto):
            elemento.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def preencher_dados_iniciais(self, cpf_titular):
        """
        Preenche os 3 campos iniciais e clica em Continuar
        
        Args:
            cpf_titular: CPF do titular a ser preenchido
        """
        print("\n📝 Preenchendo dados iniciais...")
        
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
                    WebDriverWait(self.driver, 5).until(
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
            self.digitar_devagar(campo_data, "03/2025")
            print("   ✅ Data: 03/2025")
            self.delay_humano(0.5, 1.0)
            
            # CAMPO 2: CNPJ
            print("   🏢 Preenchendo CNPJ...")
            campo_cnpj = self.driver.find_element(By.ID, "insc_estabelecimento")
            campo_cnpj.clear()
            self.delay_humano(0.2, 0.5)
            self.digitar_devagar(campo_cnpj, "19.310.796/0001-07")
            print("   ✅ CNPJ: 19.310.796/0001-07")
            self.delay_humano(0.5, 1.0)
            
            # CAMPO 3: CPF do Beneficiário
            print(f"   👤 Preenchendo CPF do Beneficiário...")
            campo_cpf = self.driver.find_element(By.ID, "cpf_beneficiario")
            campo_cpf.clear()
            self.delay_humano(0.2, 0.5)
            self.digitar_devagar(campo_cpf, cpf_titular)
            print(f"   ✅ CPF: {cpf_titular}")
            self.delay_humano(0.8, 1.5)
            
            # BOTÃO: Continuar
            print("   🔘 Clicando em 'Continuar'...")
            botao_continuar = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="botao_continuar"]')
            botao_continuar.click()
            print("   ✅ Clicado em Continuar")
            self.delay_humano(1.5, 2.5)
            
            print("\n✅ Dados iniciais preenchidos com sucesso!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro ao preencher dados iniciais: {e}")
            return False
    
    def preencher_formulario(self, cpf_titular):
        """Preenche o formulário automaticamente"""
        print("\n" + "="*60)
        print("🤖 INICIANDO PREENCHIMENTO AUTOMÁTICO")
        print("="*60)
        
        # Preencher primeira parte (3 campos + botão)
        if not self.preencher_dados_iniciais(cpf_titular):
            print("❌ Falha no preenchimento inicial")
            return False
        
        # TODO: Próximas etapas serão adicionadas conforme suas instruções
        print("\n✅ Primeira etapa concluída!")
        print("\n⏸️ Aguardando próximas instruções...")
        print("Me diga o que vem DEPOIS de clicar em 'Continuar'!")
        
        input("\nPressione ENTER para continuar...")
    
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
    
    def executar(self):
        """Função principal de execução"""
        print("\n" + "="*60)
        print("🤖 AUTOMAÇÃO EFD-REINF")
        print("="*60)
        print("\n💡 FUNCIONAMENTO:")
        print("   1. Chrome abre no site")
        print("   2. VOCÊ faz login e navega até o formulário")
        print("   3. CÓDIGO preenche automaticamente")
        print("="*60)
        
        # Carregar dados do Excel
        cpf_titular = self.carregar_dados()
        if not cpf_titular:
            print("❌ Não foi possível carregar dados")
            return
        
        # Abrir site
        self.abrir_site()
        
        # Aguardar login e navegação manual
        self.aguardar_login()
        
        # Preencher formulário automaticamente
        self.preencher_formulario(cpf_titular)
        
        print("\n✅ Processo concluído!")
        input("\nPressione ENTER para encerrar...")

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

