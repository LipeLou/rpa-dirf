"""
Assistente EFD-REINF - Preenchimento AUTOMÁTICO + Envio MANUAL
Sistema preenche tudo, você apenas revisa e envia
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import time
import pandas as pd
import os
import sys
import platform
import random

# Configurar encoding UTF-8
if platform.system() == "Windows":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configurações
url_base = 'http://www3.cav.receita.fazenda.gov.br/reinfweb/#/home'
data_padrao = '03/2025'
cnpj_padrao = '19.310.796/0001-07'
operadora_padrao = '23.802.218/0001-65'

# Mapeamento de dependências
MAPA_DEPENDENCIAS = {
    'Titular': 'Titular',
    'Esposa': 'Cônjuge',
    'Esposo': 'Cônjuge',
    'Filho': 'Filho(a) ou enteado(a)',
    'Filha': 'Filho(a) ou enteado(a)',
    'Companheiro(a)': 'Companheiro(a) com o(a) qual tenha filho ou viva há mais de 5 (cinco) anos ou possua declaração de união estável',
    'Mae': 'Pais, avós e bisavós',
    'Mãe': 'Pais, avós e bisavós',
    'Pai': 'Pais, avós e bisavós',
    'Agregado': 'Agregado/Outros',
    'Sogra': 'Agregado/Outros',
    'Sogro': 'Agregado/Outros',
    'Outra Dependencia': 'Agregado/Outros'
}

def formatar_valor(valor):
    """Formata valor para padrão brasileiro"""
    try:
        if isinstance(valor, str):
            valor = valor.replace(',', '.')
        if pd.isna(valor) or valor == '' or valor is None:
            return '0,00'
        return f"{float(valor):.2f}".replace('.', ',')
    except:
        return '0,00'

class AssistenteAutomatico:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura Chrome"""
        print("\n🔧 Configurando Chrome...")
        
        profile_dir = os.path.join(os.getcwd(), "chrome_assistente")
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        
        options = uc.ChromeOptions()
        options.add_argument(f'--user-data-dir={profile_dir}')
        options.add_argument('--start-maximized')
        
        print("🚀 Abrindo Chrome...")
        self.driver = uc.Chrome(options=options, use_subprocess=True)
        
        stealth(self.driver,
            languages=["pt-BR", "pt"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        
        print("✅ Chrome aberto!")
        print(f"🌐 Navegando para: {url_base}")
        self.driver.get(url_base)
        print("✅ Site carregado!")
    
    def delay(self, min_sec=0.3, max_sec=0.8):
        """Delay humano"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def digitar_devagar(self, elemento, texto):
        """Digita como humano"""
        for char in str(texto):
            elemento.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def janela_ativa(self):
        """Verifica se Chrome está ativo"""
        try:
            _ = self.driver.current_url
            return True
        except:
            return False
    
    def tentar_preencher_campo(self, by, locator, valor, nome_campo):
        """Tenta preencher um campo, retorna True se sucesso"""
        try:
            if not self.janela_ativa():
                print(f"   ⚠️ {nome_campo}: Chrome não está ativo")
                return False
            
            elemento = self.driver.find_element(by, locator)
            elemento.clear()
            self.delay(0.2, 0.4)
            self.digitar_devagar(elemento, valor)
            print(f"   ✅ {nome_campo}: {valor}")
            self.delay(0.5, 1.0)
            return True
        except Exception as e:
            print(f"   ⚠️ {nome_campo}: Preencha manualmente → {valor}")
            return False
    
    def tentar_selecionar(self, by, locator, texto, nome_campo):
        """Tenta selecionar opção em dropdown"""
        try:
            if not self.janela_ativa():
                print(f"   ⚠️ {nome_campo}: Chrome não está ativo")
                return False
            
            select = Select(self.driver.find_element(by, locator))
            select.select_by_visible_text(texto)
            print(f"   ✅ {nome_campo}: {texto}")
            self.delay(0.5, 1.0)
            return True
        except Exception as e:
            print(f"   ⚠️ {nome_campo}: Selecione manualmente → {texto}")
            return False
    
    def tentar_clicar(self, by, locator, nome_botao):
        """Tenta clicar em botão"""
        try:
            if not self.janela_ativa():
                print(f"   ⚠️ {nome_botao}: Chrome não está ativo")
                return False
            
            elemento = self.driver.find_element(by, locator)
            elemento.click()
            print(f"   ✅ Clicado: {nome_botao}")
            self.delay(1.0, 2.0)
            return True
        except Exception as e:
            print(f"   ⚠️ Clique manualmente: {nome_botao}")
            return False
    
    def preencher_dados_iniciais(self, cpf_titular):
        """Preenche dados iniciais do formulário"""
        print("\n🤖 Preenchendo dados iniciais...")
        
        self.delay(0.5, 1.0)
        
        # Data
        self.tentar_preencher_campo(By.ID, "periodo_apuracao", data_padrao, "Data")
        
        # CNPJ
        self.tentar_preencher_campo(By.ID, "insc_estabelecimento", cnpj_padrao, "CNPJ")
        
        # CPF
        self.tentar_preencher_campo(By.ID, "cpf_beneficiario", cpf_titular, "CPF Titular")
        
        print("\n📋 Dados iniciais preenchidos!")
        print("👁️ REVISE os campos preenchidos")
        print("🖱️ Clique em 'Continuar' para próxima etapa")
        input("\n✅ Pressione ENTER após clicar em Continuar...")
    
    def adicionar_dependente(self, cpf, relacao):
        """Adiciona um dependente"""
        print(f"\n➕ Adicionando dependente {cpf}...")
        
        # Clicar em adicionar (se houver botão)
        print("   🖱️ Procurando botão 'Adicionar Dependente'...")
        if not self.tentar_clicar(By.ID, 'BotaoInclusaoDiv_ideDep', 'Adicionar Dependente'):
            print("   ⏸️ Clique manualmente em 'Adicionar Dependente'")
            input("   ✅ Pressione ENTER após clicar...")
        
        self.delay(0.5, 1.0)
        
        # Preencher CPF
        self.tentar_preencher_campo(By.ID, "ideDep", cpf, "CPF Dependente")
        
        # Selecionar relação
        self.tentar_selecionar(By.ID, "naturezaDependencia", relacao, "Relação")
        
        # Preencher Agregado/Outros se necessário
        if relacao == 'Agregado/Outros':
            print("   ⏸️ Campo 'Agregado/Outros' pode estar visível")
            print("   ⏸️ Se sim, preencha a descrição manualmente")
            input("   ✅ Pressione ENTER se preencheu (ou se não havia campo)...")
        
        print("\n   👁️ REVISE os dados do dependente")
        print("   🖱️ Clique em 'Confirmar' ou 'OK'")
        input("\n   ✅ Pressione ENTER após confirmar o dependente...")
    
    def processar_grupo(self, grupo):
        """Processa um grupo completo"""
        titular = grupo[0]
        dependentes = grupo[1:] if len(grupo) > 1 else []
        
        # Mostrar dados
        print("\n" + "="*70)
        print("📋 DADOS DO GRUPO")
        print("="*70)
        print(f"\n👤 TITULAR: {titular['NOME']}")
        print(f"   CPF: {titular['CPF']}")
        
        print(f"\n💰 VALORES:")
        print(f"   Mensalidade: R$ {formatar_valor(titular.get('MENSALIDADE', 0))}")
        print(f"   Consulta: R$ {formatar_valor(titular.get('CONSULTA', 0))}")
        print(f"   Total Titular: R$ {formatar_valor(titular.get('TOTAL', 0))}")
        
        if dependentes:
            print(f"\n👥 DEPENDENTES ({len(dependentes)}):")
            for i, dep in enumerate(dependentes):
                relacao = dep.get('DEPENDENCIA', 'N/A')
                relacao_map = MAPA_DEPENDENCIAS.get(relacao, 'Agregado/Outros')
                print(f"   {i+1}. {dep['NOME']}")
                print(f"      CPF: {dep['CPF']}")
                print(f"      Relação: {relacao_map}")
                print(f"      Valor: R$ {formatar_valor(dep.get('TOTAL', 0))}")
        
        print("\n" + "="*70)
        
        # PASSO 1: Abrir formulário
        print("\n📍 PASSO 1 - ABRIR FORMULÁRIO")
        print("   🖱️ No Chrome: Clique em 'Incluir Pagamento/Crédito'")
        print("   ⏰ Aguarde o formulário carregar")
        input("\n✅ Pressione ENTER quando FORMULÁRIO estiver aberto...")
        
        if not self.janela_ativa():
            print("❌ Chrome fechou ou perdeu conexão")
            return False
        
        # PASSO 2: Preencher dados iniciais AUTOMATICAMENTE
        print("\n📍 PASSO 2 - PREENCHIMENTO AUTOMÁTICO")
        self.preencher_dados_iniciais(titular['CPF'])
        
        if not self.janela_ativa():
            print("❌ Chrome fechou. Continue manualmente ou reinicie.")
            return False
        
        # PASSO 3: Adicionar dependentes AUTOMATICAMENTE
        if dependentes:
            print(f"\n📍 PASSO 3 - ADICIONANDO {len(dependentes)} DEPENDENTE(S)")
            
            for i, dep in enumerate(dependentes):
                relacao = dep.get('DEPENDENCIA', 'N/A')
                relacao_map = MAPA_DEPENDENCIAS.get(relacao, 'Agregado/Outros')
                
                print(f"\n   --- Dependente {i+1}/{len(dependentes)}: {dep['NOME']} ---")
                
                self.adicionar_dependente(dep['CPF'], relacao_map)
                
                if not self.janela_ativa():
                    print("   ❌ Chrome fechou. Continue manualmente.")
                    return False
        
        # PASSO 4: Valores e ENVIO MANUAL
        print("\n📍 PASSO 4 - VALORES E ENVIO MANUAL")
        print("\n💰 VALORES PARA CONFERIR:")
        print(f"   Operadora: {operadora_padrao}")
        print(f"\n   Titular: R$ {formatar_valor(titular.get('TOTAL', 0))}")
        
        if dependentes:
            print(f"   Dependentes:")
            for dep in dependentes:
                print(f"      {dep['NOME']}: R$ {formatar_valor(dep.get('TOTAL', 0))}")
        
        print("\n" + "="*70)
        print("⏸️ AGORA VOCÊ FAZ MANUALMENTE:")
        print("="*70)
        print("1. 💊 Adicione plano de saúde (se houver campo)")
        print(f"   - Operadora: {operadora_padrao}")
        print("2. 💰 Adicione/confira os valores mostrados acima")
        print("3. 👁️ REVISE TUDO com atenção:")
        print("   - Titular está correto?")
        print("   - Dependentes foram adicionados?")
        print("   - Valores estão corretos?")
        print("4. 📤 Clique em 'ENVIAR' ou 'FINALIZAR'")
        print("5. ⏰ Aguarde confirmação de envio")
        print("="*70)
        
        input("\n✅ Pressione ENTER quando ENVIAR e ver confirmação...")
        
        print(f"\n🎉 Grupo de {titular['NOME']} CONCLUÍDO!")
        
        # Voltar ao menu (se necessário)
        print("\n🔄 Voltando ao menu principal...")
        try:
            self.driver.get(url_base)
            self.delay(2.0, 3.0)
        except:
            print("   ⏸️ Navegue manualmente de volta ao menu")
            input("   ✅ Pressione ENTER quando estiver no menu...")
        
        return True
    
    def executar(self):
        """Executa o assistente"""
        print("="*70)
        print("🤖 ASSISTENTE AUTOMÁTICO - Preenche campos, você envia")
        print("="*70)
        print("\n✨ FUNCIONAMENTO:")
        print("   ✅ Sistema PREENCHE campos automaticamente")
        print("   ✅ VOCÊ revisa tudo")
        print("   ✅ VOCÊ envia manualmente")
        print("   → Rápido + Seguro + Sem erros em lote!")
        print("="*70)
        
        # Ler dados
        print("\n📂 Lendo Excel...")
        try:
            dados = pd.read_excel('dados.xlsx', sheet_name='MAR 2025', skiprows=1)
            dados_limpos = dados.dropna(how='all')
            dados_limpos = dados_limpos[dados_limpos['CPF'].notna()]
            print(f"✅ {len(dados_limpos)} registros")
        except Exception as e:
            print(f"❌ Erro ao ler Excel: {e}")
            return
        
        # Agrupar
        print("📊 Agrupando...")
        grupos = []
        titulares = dados_limpos[dados_limpos['DEPENDENCIA'] == 'Titular']
        
        for _, titular in titulares.iterrows():
            grupo = [titular.to_dict()]
            cod_familia = titular['CÓD DA FAMILIA']
            deps = dados_limpos[
                (dados_limpos['CÓD DA FAMILIA'] == cod_familia) & 
                (dados_limpos['DEPENDENCIA'] != 'Titular')
            ]
            for _, dep in deps.iterrows():
                grupo.append(dep.to_dict())
            grupos.append(grupo)
        
        print(f"✅ {len(grupos)} grupos\n")
        
        # Login
        print("="*70)
        print("🔐 FAÇA LOGIN")
        print("="*70)
        print("1. Chrome está aberto no site")
        print("2. Faça LOGIN com certificado digital")
        print("3. Vá para a TELA PRINCIPAL")
        print("="*70)
        input("\n✅ Pressione ENTER quando estiver LOGADO...")
        
        # Processar grupos
        processados = 0
        pulados = 0
        
        for i, grupo in enumerate(grupos):
            titular = grupo[0]
            
            if not self.janela_ativa():
                print("\n❌ Chrome fechou! Encerrando...")
                break
            
            print(f"\n{'='*70}")
            print(f"📌 GRUPO {i+1}/{len(grupos)} - {titular['NOME']}")
            print(f"{'='*70}")
            
            print("\n❓ Deseja processar?")
            print("   [S] Sim [N] Não [P] Pausar [D] Ver detalhes")
            
            escolha = input("\n➤ ").strip().upper()
            
            if escolha == 'P':
                print("\n⏸️ Pausado")
                break
            elif escolha == 'N':
                pulados += 1
                continue
            elif escolha == 'D':
                self.mostrar_detalhes(grupo)
                input("\nPressione ENTER para voltar...")
                # Não incrementar, vai mostrar o grupo novamente
                escolha = 'S'  # Processar após mostrar detalhes
            
            if escolha == 'S':
                try:
                    if self.processar_grupo(grupo):
                        processados += 1
                except Exception as e:
                    print(f"\n❌ Erro: {e}")
                    print("💡 Continue manualmente ou pule este grupo")
                    input("Pressione ENTER...")
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO")
        print("="*70)
        print(f"Total: {len(grupos)}")
        print(f"✅ Processados: {processados}")
        print(f"⏭️ Pulados: {pulados}")
        print(f"⏸️ Restantes: {len(grupos) - processados - pulados}")
        print("="*70)
    
    def mostrar_detalhes(self, grupo):
        """Mostra detalhes completos"""
        titular = grupo[0]
        dependentes = grupo[1:] if len(grupo) > 1 else []
        
        print("\n" + "="*70)
        print("📊 DETALHES COMPLETOS")
        print("="*70)
        print(f"\n👤 TITULAR: {titular['NOME']}")
        print(f"   CPF: {titular['CPF']}")
        print(f"   Nascimento: {titular.get('NASCIMENTO', 'N/A')}")
        print(f"   Código Família: {titular.get('CÓD DA FAMILIA', 'N/A')}")
        
        print(f"\n💰 VALORES TITULAR:")
        print(f"   Mensalidade: R$ {formatar_valor(titular.get('MENSALIDADE', 0))}")
        print(f"   Consulta: R$ {formatar_valor(titular.get('CONSULTA', 0))}")
        print(f"   Retroativo RN: R$ {formatar_valor(titular.get('RETROATIVO RN', 0))}")
        print(f"   Retroativo: R$ {formatar_valor(titular.get('RETROATIVO', 0))}")
        print(f"   TOTAL: R$ {formatar_valor(titular.get('TOTAL', 0))}")
        
        if dependentes:
            print(f"\n👥 DEPENDENTES ({len(dependentes)}):")
            for i, dep in enumerate(dependentes):
                relacao = dep.get('DEPENDENCIA', 'N/A')
                relacao_map = MAPA_DEPENDENCIAS.get(relacao, 'Agregado/Outros')
                print(f"\n   {i+1}. {dep['NOME']}")
                print(f"      CPF: {dep['CPF']}")
                print(f"      Nascimento: {dep.get('NASCIMENTO', 'N/A')}")
                print(f"      Relação: {relacao} → {relacao_map}")
                print(f"      Mensalidade: R$ {formatar_valor(dep.get('MENSALIDADE', 0))}")
                print(f"      Consulta: R$ {formatar_valor(dep.get('CONSULTA', 0))}")
                print(f"      TOTAL: R$ {formatar_valor(dep.get('TOTAL', 0))}")
        
        print("\n📝 RESUMO PARA PREENCHER:")
        print(f"   Data: {data_padrao}")
        print(f"   CNPJ: {cnpj_padrao}")
        print(f"   CPF Titular: {titular['CPF']}")
        print(f"   Operadora: {operadora_padrao}")
        print(f"   Dependentes: {len(dependentes)}")
        print("="*70)
    
    def fechar(self):
        """Fecha navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def main():
    print("\n" + "="*70)
    print("🚀 ASSISTENTE COM PREENCHIMENTO AUTOMÁTICO")
    print("="*70)
    print("\n⚡ O sistema vai:")
    print("   ✅ Preencher Data, CNPJ, CPF automaticamente")
    print("   ✅ Adicionar dependentes automaticamente")
    print("   ✅ Mostrar valores para conferir")
    print("   ⏸️ VOCÊ revisa e envia manualmente")
    print("\n🎯 Melhor dos dois mundos: Rápido + Seguro!")
    print("="*70)
    
    assistente = None
    
    try:
        assistente = AssistenteAutomatico()
        assistente.executar()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido (CTRL+C)")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if assistente:
            assistente.fechar()
        
        print("\n" + "="*70)
        print("👋 ENCERRADO")
        print("="*70)
        input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    main()

