#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Checkpoint EFD-REINF
Permite visualizar e gerenciar o progresso da automação
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

# Importar configurações
from config import BANCO_DADOS

class GerenciadorCheckpoint:
    """
    Gerenciador completo de checkpoints para automação EFD-REINF.
    
    Esta classe fornece interface completa para visualizar, gerenciar e controlar
    o progresso da automação através do banco de dados SQLite.
    
    Funcionalidades principais:
    - Visualização de status geral e estatísticas
    - Consulta detalhada de CPFs processados
    - Exportação de relatórios em Excel
    - Reset e alteração de checkpoints
    - Limpeza seletiva de dados
    - Geração de planilhas de visualização
    
    Attributes:
        banco_dados (str): Caminho para o arquivo do banco SQLite
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de checkpoint.
        
        Configura a conexão com o banco de dados SQLite que armazena
        todo o progresso da automação EFD-REINF.
        """
        self.banco_dados = BANCO_DADOS
    
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        try:
            conn = sqlite3.connect(self.banco_dados)
            return conn
        except Exception as e:
            print(f"❌ Erro ao conectar banco: {e}")
            return None
    
    def mostrar_menu(self):
        """Mostra o menu principal"""
        print("\n" + "="*60)
        print("📊 GERENCIADOR DE CHECKPOINT EFD-REINF")
        print("="*60)
        print("1. 📋 Ver status geral")
        print("2. 👤 Ver CPFs processados")
        print("3. 🔍 Buscar CPF específico")
        print("4. 📈 Ver estatísticas")
        print("5. 🗑️ Limpar dados")
        print("6. 📋 Gerar planilha de visualização")
        print("7. ⚙️ Alterar checkpoint atual")
        print("0. ❌ Sair")
        print("="*60)
    
    def ver_status_geral(self):
        """Mostra status geral do banco"""
        try:
            conn = self.conectar_banco()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Contar registros por tabela
            tabelas = [
                'progresso_efd',
                'dependentes_processados', 
                'planos_processados',
                'info_dependentes_processados'
            ]
            
            print(f"\n📊 STATUS GERAL DO BANCO DE DADOS")
            print(f"{'='*50}")
            
            for tabela in tabelas:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {tabela}')
                    total = cursor.fetchone()[0]
                    print(f"{tabela:30} | {total:5} registros")
                except:
                    print(f"{tabela:30} | Tabela não existe")
            
            # Últimos 10 registros de progresso
            cursor.execute('''
                SELECT cpf_titular, nome_titular, etapa_atual, status, timestamp 
                FROM progresso_efd 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            ultimos = cursor.fetchall()
            
            if ultimos:
                print(f"\n🕒 ÚLTIMOS 10 REGISTROS:")
                print(f"{'CPF':15} | {'Nome':20} | {'Etapa':20} | {'Status':10} | {'Data/Hora'}")
                print("-" * 90)
                for registro in ultimos:
                    cpf, nome, etapa, status, timestamp = registro
                    nome_curto = nome[:18] + ".." if len(nome) > 20 else nome
                    etapa_curta = etapa[:18] + ".." if len(etapa) > 20 else etapa
                    print(f"{cpf:15} | {nome_curto:20} | {etapa_curta:20} | {status:10} | {timestamp}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao ver status: {e}")
    
    def ver_cpfs_processados(self):
        """Mostra todos os CPFs processados"""
        try:
            conn = self.conectar_banco()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Buscar todos os CPFs únicos
            cursor.execute('''
                SELECT DISTINCT cpf_titular, nome_titular,
                       MAX(timestamp) as ultima_atualizacao,
                       COUNT(*) as total_registros
                FROM progresso_efd 
                GROUP BY cpf_titular, nome_titular
                ORDER BY ultima_atualizacao DESC
            ''')
            
            cpfs = cursor.fetchall()
            
            if not cpfs:
                print("\n❌ Nenhum CPF encontrado no banco")
                return
            
            print(f"\n👤 CPFs PROCESSADOS ({len(cpfs)} encontrados)")
            print(f"{'='*80}")
            print(f"{'CPF':15} | {'Nome':25} | {'Status':12} | {'Registros':9} | {'Última Atualização'}")
            print("-" * 80)
            
            for cpf, nome, ultima_atualizacao, total_registros in cpfs:
                # Buscar status mais recente
                cursor.execute('''
                    SELECT status FROM progresso_efd 
                    WHERE cpf_titular = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ''', (cpf,))
                status_result = cursor.fetchone()
                status = status_result[0] if status_result else "N/A"
                
                nome_curto = nome[:23] + ".." if len(nome) > 25 else nome
                print(f"{cpf:15} | {nome_curto:25} | {status:12} | {total_registros:9} | {ultima_atualizacao}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao ver CPFs: {e}")
    
    def buscar_cpf_especifico(self):
        """Busca informações de um CPF específico"""
        try:
            cpf = input("\n🔍 Digite o CPF para buscar: ").strip()
            if not cpf:
                print("❌ CPF não informado")
                return
            
            conn = self.conectar_banco()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Buscar progresso do CPF
            cursor.execute('''
                SELECT etapa_atual, status, timestamp, observacoes
                FROM progresso_efd 
                WHERE cpf_titular = ?
                ORDER BY timestamp DESC
            ''', (cpf,))
            
            progressos = cursor.fetchall()
            
            if not progressos:
                print(f"\n❌ CPF {cpf} não encontrado no banco")
                conn.close()
                return
            
            print(f"\n🔍 DETALHES DO CPF: {cpf}")
            print(f"{'='*60}")
            
            for i, (etapa, status, timestamp, observacoes) in enumerate(progressos, 1):
                print(f"\n📋 Registro {i}:")
                print(f"   Etapa: {etapa}")
                print(f"   Status: {status}")
                print(f"   Data/Hora: {timestamp}")
                if observacoes:
                    print(f"   Observações: {observacoes}")
            
            # Buscar dependentes processados
            cursor.execute('''
                SELECT cpf_dependente, relacao, status, timestamp
                FROM dependentes_processados 
                WHERE cpf_titular = ?
                ORDER BY timestamp DESC
            ''', (cpf,))
            
            dependentes = cursor.fetchall()
            
            if dependentes:
                print(f"\n👥 DEPENDENTES PROCESSADOS ({len(dependentes)}):")
                for dep_cpf, relacao, status, timestamp in dependentes:
                    print(f"   CPF: {dep_cpf} | Relação: {relacao} | Status: {status} | {timestamp}")
            
            # Buscar planos processados
            cursor.execute('''
                SELECT cnpj_operadora, valor_titular, status, timestamp
                FROM planos_processados 
                WHERE cpf_titular = ?
                ORDER BY timestamp DESC
            ''', (cpf,))
            
            planos = cursor.fetchall()
            
            if planos:
                print(f"\n🏥 PLANOS PROCESSADOS ({len(planos)}):")
                for cnpj, valor, status, timestamp in planos:
                    print(f"   CNPJ: {cnpj} | Valor: {valor} | Status: {status} | {timestamp}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao buscar CPF: {e}")
    
    def ver_estatisticas(self):
        """Mostra estatísticas detalhadas"""
        try:
            conn = self.conectar_banco()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            print(f"\n📈 ESTATÍSTICAS DETALHADAS")
            print(f"{'='*50}")
            
            # Estatísticas por status
            cursor.execute('''
                SELECT status, COUNT(*) as total
                FROM progresso_efd 
                GROUP BY status
                ORDER BY total DESC
            ''')
            
            status_stats = cursor.fetchall()
            
            print(f"\n📊 Por Status:")
            for status, total in status_stats:
                print(f"   {status:15} | {total:5} registros")
            
            # Estatísticas por etapa
            cursor.execute('''
                SELECT etapa_atual, COUNT(*) as total
                FROM progresso_efd 
                GROUP BY etapa_atual
                ORDER BY total DESC
            ''')
            
            etapa_stats = cursor.fetchall()
            
            print(f"\n📋 Por Etapa:")
            for etapa, total in etapa_stats:
                print(f"   {etapa:25} | {total:5} registros")
            
            # CPFs únicos
            cursor.execute('SELECT COUNT(DISTINCT cpf_titular) FROM progresso_efd')
            cpfs_unicos = cursor.fetchone()[0]
            
            print(f"\n👤 Total de CPFs únicos: {cpfs_unicos}")
            
            # Data do primeiro e último registro
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM progresso_efd')
            primeiro, ultimo = cursor.fetchone()
            
            if primeiro and ultimo:
                print(f"📅 Primeiro registro: {primeiro}")
                print(f"📅 Último registro: {ultimo}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao ver estatísticas: {e}")
    
    def verificar_tabela_existe(self, cursor, tabela):
        """Verifica se uma tabela existe no banco"""
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (tabela,))
        return cursor.fetchone() is not None
    
    def criar_tabelas_se_nao_existirem(self, cursor):
        """Cria todas as tabelas necessárias se não existirem"""
        tabelas = [
            ('progresso_efd', '''
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
            '''),
            ('dependentes_processados', '''
                CREATE TABLE IF NOT EXISTS dependentes_processados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf_titular TEXT NOT NULL,
                    cpf_dependente TEXT NOT NULL,
                    relacao TEXT,
                    descricao_agregado TEXT,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            '''),
            ('planos_processados', '''
                CREATE TABLE IF NOT EXISTS planos_processados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf_titular TEXT NOT NULL,
                    cnpj_operadora TEXT NOT NULL,
                    valor_titular TEXT,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            '''),
            ('info_dependentes_processados', '''
                CREATE TABLE IF NOT EXISTS info_dependentes_processados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf_titular TEXT NOT NULL,
                    cpf_dependente TEXT NOT NULL,
                    valor_dependente TEXT,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            '''),
            ('checkpoint_indice', '''
                CREATE TABLE IF NOT EXISTS checkpoint_indice (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ultimo_indice INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        ]
        
        for nome_tabela, create_sql in tabelas:
            cursor.execute(create_sql)
    
    def limpar_dados(self):
        """Limpa dados do banco"""
        try:
            print(f"\n🗑️ LIMPEZA DE DADOS")
            print(f"{'='*40}")
            print("1. Limpar TUDO")
            print("2. Limpar CPF específico")
            print("3. Limpar registros antigos")
            print("0. Voltar")
            
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == "1":
                confirmar = input("⚠️ Tem certeza que quer limpar TUDO? (digite 'SIM' para confirmar): ")
                if confirmar == "SIM":
                    conn = self.conectar_banco()
                    if conn:
                        cursor = conn.cursor()
                        
                        # Criar tabelas se não existirem
                        self.criar_tabelas_se_nao_existirem(cursor)
                        
                        # Agora limpar os dados
                        cursor.execute('DELETE FROM progresso_efd')
                        cursor.execute('DELETE FROM dependentes_processados')
                        cursor.execute('DELETE FROM planos_processados')
                        cursor.execute('DELETE FROM info_dependentes_processados')
                        cursor.execute('DELETE FROM checkpoint_indice')
                        conn.commit()
                        conn.close()
                        print("✅ Todos os dados foram limpos!")
                        print("💡 Checkpoint de índice também foi resetado - processamento começará do início")
                    else:
                        print("❌ Erro ao conectar banco")
                else:
                    print("❌ Operação cancelada")
            
            elif opcao == "2":
                cpf = input("Digite o CPF para limpar: ").strip()
                if cpf:
                    conn = self.conectar_banco()
                    if conn:
                        cursor = conn.cursor()
                        
                        # Criar tabelas se não existirem
                        self.criar_tabelas_se_nao_existirem(cursor)
                        
                        cursor.execute('DELETE FROM progresso_efd WHERE cpf_titular = ?', (cpf,))
                        cursor.execute('DELETE FROM dependentes_processados WHERE cpf_titular = ?', (cpf,))
                        cursor.execute('DELETE FROM planos_processados WHERE cpf_titular = ?', (cpf,))
                        cursor.execute('DELETE FROM info_dependentes_processados WHERE cpf_titular = ?', (cpf,))
                        conn.commit()
                        conn.close()
                        print(f"✅ Dados do CPF {cpf} foram limpos!")
                    else:
                        print("❌ Erro ao conectar banco")
            
            elif opcao == "3":
                dias = input("Digite quantos dias atrás limpar (ex: 7): ").strip()
                try:
                    dias = int(dias)
                    conn = self.conectar_banco()
                    if conn:
                        cursor = conn.cursor()
                        
                        # Criar tabelas se não existirem
                        self.criar_tabelas_se_nao_existirem(cursor)
                        
                        cursor.execute('''
                            DELETE FROM progresso_efd 
                            WHERE timestamp < datetime('now', '-{} days')
                        '''.format(dias))
                        cursor.execute('''
                            DELETE FROM dependentes_processados 
                            WHERE timestamp < datetime('now', '-{} days')
                        '''.format(dias))
                        cursor.execute('''
                            DELETE FROM planos_processados 
                            WHERE timestamp < datetime('now', '-{} days')
                        '''.format(dias))
                        cursor.execute('''
                            DELETE FROM info_dependentes_processados 
                            WHERE timestamp < datetime('now', '-{} days')
                        '''.format(dias))
                        conn.commit()
                        conn.close()
                        print(f"✅ Registros anteriores a {dias} dias foram limpos!")
                    else:
                        print("❌ Erro ao conectar banco")
                except ValueError:
                    print("❌ Número de dias inválido")
            
        except Exception as e:
            print(f"❌ Erro ao limpar dados: {e}")
    
    def gerar_planilha_visualizacao(self):
        """Gera planilha Excel para visualização do banco de dados"""
        try:
            print("\n📊 Gerando planilha de visualização...")
            
            conn = self.conectar_banco()
            if not conn:
                return
            
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
            
        except Exception as e:
            print(f"❌ Erro ao gerar planilha: {e}")
    
    def alterar_checkpoint_atual(self):
        """Menu para alterar o checkpoint atual"""
        try:
            print(f"\n⚙️ ALTERAR CHECKPOINT ATUAL")
            print(f"{'='*50}")
            print("1. 📊 Alterar por número de grupo")
            print("2. 👤 Alterar por CPF específico")
            print("3. 📋 Ver checkpoint atual")
            print("4. 📄 Listar grupos disponíveis")
            print("0. ⬅️ Voltar")
            
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == "1":
                self.alterar_checkpoint_por_indice()
            elif opcao == "2":
                self.alterar_checkpoint_por_cpf()
            elif opcao == "3":
                self.ver_checkpoint_atual()
            elif opcao == "4":
                self.listar_grupos_disponiveis()
            elif opcao == "0":
                return
            else:
                print("❌ Opção inválida")
                
        except Exception as e:
            print(f"❌ Erro ao alterar checkpoint: {e}")
    
    def ver_checkpoint_atual(self):
        """Mostra o checkpoint atual"""
        try:
            conn = self.conectar_banco()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            print(f"\n📋 CHECKPOINT ATUAL")
            print(f"{'='*40}")
            
            # Ver checkpoint de grupo
            try:
                cursor.execute('SELECT ultimo_indice, timestamp FROM checkpoint_indice ORDER BY timestamp DESC LIMIT 1')
                checkpoint = cursor.fetchone()
                if checkpoint:
                    indice, timestamp = checkpoint
                    numero_grupo = indice + 1
                    print(f"📊 Checkpoint: Grupo {numero_grupo}")
                    print(f"   Atualizado em: {timestamp}")
                else:
                    print("📊 Checkpoint: Não definido (começará do grupo 1)")
            except:
                print("📊 Checkpoint: Tabela não existe")
            
            # Ver último CPF processado
            try:
                cursor.execute('''
                    SELECT cpf_titular, nome_titular, etapa_atual, status, timestamp 
                    FROM progresso_efd 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ''')
                ultimo_cpf = cursor.fetchone()
                if ultimo_cpf:
                    cpf, nome, etapa, status, timestamp = ultimo_cpf
                    print(f"\n👤 Último CPF processado: {cpf}")
                    print(f"   Nome: {nome}")
                    print(f"   Etapa: {etapa}")
                    print(f"   Status: {status}")
                    print(f"   Data: {timestamp}")
                else:
                    print("\n👤 Nenhum CPF processado ainda")
            except:
                print("\n👤 Tabela de progresso não existe")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao ver checkpoint atual: {e}")
    
    def listar_grupos_disponiveis(self):
        """Lista os grupos disponíveis no Excel"""
        try:
            arquivo_excel = 'dados.xlsx'
            planilha = 'MAR 2025'
            
            if not os.path.exists(arquivo_excel):
                print(f"❌ Arquivo {arquivo_excel} não encontrado")
                return
            
            print(f"\n📄 GRUPOS DISPONÍVEIS EM {arquivo_excel}")
            print(f"{'='*60}")
            
            # Ler dados do Excel
            dados = pd.read_excel(arquivo_excel, sheet_name=planilha, skiprows=1)
            dados_limpos = dados.dropna(how='all')
            dados_limpos = dados_limpos[dados_limpos['CPF'].notna()]
            
            # Agrupar por titular
            grupos = []
            grupo_atual = []
            
            for _, row in dados_limpos.iterrows():
                if pd.isna(row['NOME']) or str(row['NOME']).strip() == '':
                    continue
                if pd.isna(row['DEPENDENCIA']) or str(row['DEPENDENCIA']).strip() == '':
                    continue
                if pd.isna(row['CPF']) or str(row['CPF']).strip() == '':
                    continue
                
                dependencia = str(row['DEPENDENCIA']).strip().upper()
                
                if dependencia == 'TITULAR':
                    if grupo_atual:
                        grupos.append(grupo_atual)
                    grupo_atual = [row]
                else:
                    if grupo_atual:
                        grupo_atual.append(row)
            
            if grupo_atual:
                grupos.append(grupo_atual)
            
            # Mostrar grupos
            print(f"Total de grupos encontrados: {len(grupos)}\n")
            
            for i, grupo in enumerate(grupos):
                titular = grupo[0]  # Primeiro é sempre o titular
                dependentes = len(grupo) - 1
                
                print(f"Grupo {i + 1} (índice {i}):")
                print(f"   👤 Titular: {titular['NOME']} - CPF: {titular['CPF']}")
                print(f"   👥 Dependentes: {dependentes}")
                print()
                
                # Mostrar apenas os primeiros 10 grupos para não poluir a tela
                if i >= 9:
                    restantes = len(grupos) - 10
                    if restantes > 0:
                        print(f"... e mais {restantes} grupos")
                    break
            
        except Exception as e:
            print(f"❌ Erro ao listar grupos: {e}")
    
    def alterar_checkpoint_por_indice(self):
        """Altera o checkpoint por número de grupo"""
        try:
            # Primeiro mostrar grupos disponíveis
            self.listar_grupos_disponiveis()
            
            print(f"\n⚙️ ALTERAR CHECKPOINT POR NÚMERO DE GRUPO")
            print(f"{'='*40}")
            
            try:
                numero_grupo = int(input("Digite o NÚMERO do grupo para continuar: ").strip())
            except ValueError:
                print("❌ Número inválido")
                return
            
            if numero_grupo < 1:
                print("❌ Número do grupo deve ser maior ou igual a 1")
                return
            
            # Converter número do grupo para índice (número - 1)
            novo_indice = numero_grupo - 1
            
            confirmar = input(f"⚠️ Definir checkpoint para o grupo {numero_grupo}? (digite 'SIM'): ")
            if confirmar != "SIM":
                print("❌ Operação cancelada")
                return
            
            conn = self.conectar_banco()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Criar tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkpoint_indice (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ultimo_indice INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Atualizar checkpoint (salvar o índice do grupo ANTERIOR para que o sistema processe este grupo)
            # Se queremos começar do grupo N, salvamos o índice N-1
            indice_checkpoint = max(0, novo_indice - 1)
            cursor.execute('DELETE FROM checkpoint_indice')
            cursor.execute('INSERT INTO checkpoint_indice (ultimo_indice) VALUES (?)', (indice_checkpoint,))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Checkpoint alterado para o grupo {numero_grupo}!")
            print("💡 O processamento continuará a partir deste grupo")
            
        except Exception as e:
            print(f"❌ Erro ao alterar checkpoint: {e}")
    
    def alterar_checkpoint_por_cpf(self):
        """Altera o checkpoint para um CPF específico"""
        try:
            print(f"\n⚙️ ALTERAR CHECKPOINT POR CPF")
            print(f"{'='*40}")
            
            # Mostrar CPFs disponíveis
            arquivo_excel = 'dados.xlsx'
            planilha = 'MAR 2025'
            
            if os.path.exists(arquivo_excel):
                dados = pd.read_excel(arquivo_excel, sheet_name=planilha, skiprows=1)
                titulares = dados[dados['DEPENDENCIA'] == 'TITULAR']['CPF'].tolist()
                
                print("📋 Primeiros 10 CPFs titulares no Excel:")
                for i, cpf in enumerate(titulares[:10]):
                    print(f"   {i+1}. {cpf}")
                if len(titulares) > 10:
                    print(f"   ... e mais {len(titulares) - 10} CPFs")
                print()
            
            cpf_alvo = input("Digite o CPF titular para definir como próximo: ").strip()
            if not cpf_alvo:
                print("❌ CPF não informado")
                return
            
            # Verificar se CPF existe no Excel
            if os.path.exists(arquivo_excel):
                dados = pd.read_excel(arquivo_excel, sheet_name=planilha, skiprows=1)
                cpfs_excel = dados[dados['DEPENDENCIA'] == 'TITULAR']['CPF'].astype(str).tolist()
                
                if cpf_alvo not in cpfs_excel:
                    print(f"⚠️ CPF {cpf_alvo} não encontrado como titular no Excel")
                    confirmar_mesmo_assim = input("Continuar mesmo assim? (digite 'SIM'): ")
                    if confirmar_mesmo_assim != "SIM":
                        return
                
                # Encontrar índice do grupo
                grupos = []
                grupo_atual = []
                dados_limpos = dados.dropna(how='all')
                dados_limpos = dados_limpos[dados_limpos['CPF'].notna()]
                
                for _, row in dados_limpos.iterrows():
                    if pd.isna(row['NOME']) or str(row['NOME']).strip() == '':
                        continue
                    if pd.isna(row['DEPENDENCIA']) or str(row['DEPENDENCIA']).strip() == '':
                        continue
                    if pd.isna(row['CPF']) or str(row['CPF']).strip() == '':
                        continue
                    
                    dependencia = str(row['DEPENDENCIA']).strip().upper()
                    
                    if dependencia == 'TITULAR':
                        if grupo_atual:
                            grupos.append(grupo_atual)
                        grupo_atual = [row]
                    else:
                        if grupo_atual:
                            grupo_atual.append(row)
                
                if grupo_atual:
                    grupos.append(grupo_atual)
                
                # Encontrar índice do CPF
                indice_encontrado = None
                for i, grupo in enumerate(grupos):
                    if str(grupo[0]['CPF']) == cpf_alvo:  # grupo[0] é sempre o titular
                        indice_encontrado = i
                        break
                
                if indice_encontrado is not None:
                    print(f"✅ CPF encontrado no grupo {indice_encontrado + 1} (índice {indice_encontrado})")
                    
                    confirmar = input(f"⚠️ Definir checkpoint para este CPF/grupo? (digite 'SIM'): ")
                    if confirmar != "SIM":
                        print("❌ Operação cancelada")
                        return
                    
                    conn = self.conectar_banco()
                    if not conn:
                        return
                    
                    cursor = conn.cursor()
                    
                    # Criar tabela se não existir
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS checkpoint_indice (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ultimo_indice INTEGER NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Definir checkpoint para o índice ANTERIOR ao grupo desejado
                    # Assim o sistema processará este grupo na próxima execução
                    novo_indice = max(0, indice_encontrado - 1) if indice_encontrado > 0 else 0
                    
                    cursor.execute('DELETE FROM checkpoint_indice')
                    cursor.execute('INSERT INTO checkpoint_indice (ultimo_indice) VALUES (?)', (novo_indice,))
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"✅ Checkpoint definido!")
                    print(f"💡 O processamento continuará a partir do CPF {cpf_alvo}")
                    print(f"   (Grupo {indice_encontrado + 1}, índice {indice_encontrado})")
                    
                else:
                    print(f"❌ CPF {cpf_alvo} não encontrado nos grupos")
            
        except Exception as e:
            print(f"❌ Erro ao alterar checkpoint por CPF: {e}")
    
    def executar(self):
        """Executa o gerenciador"""
        while True:
            try:
                self.mostrar_menu()
                opcao = input("\nEscolha uma opção: ").strip()
                
                if opcao == "0":
                    print("\n👋 Saindo do gerenciador...")
                    break
                elif opcao == "1":
                    self.ver_status_geral()
                elif opcao == "2":
                    self.ver_cpfs_processados()
                elif opcao == "3":
                    self.buscar_cpf_especifico()
                elif opcao == "4":
                    self.ver_estatisticas()
                elif opcao == "5":
                    self.limpar_dados()
                elif opcao == "6":
                    self.gerar_planilha_visualizacao()
                elif opcao == "7":
                    self.alterar_checkpoint_atual()
                else:
                    print("❌ Opção inválida")
                
                input("\nPressione ENTER para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Saindo do gerenciador...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    gerenciador = GerenciadorCheckpoint()
    gerenciador.executar()
