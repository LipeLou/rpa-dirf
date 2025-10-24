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

BANCO_DADOS = 'checkpoint_efd.db'

class GerenciadorCheckpoint:
    def __init__(self):
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
        print("6. 📊 Exportar relatório")
        print("7. 🔄 Resetar progresso de um CPF")
        print("8. 📋 Gerar planilha de visualização")
        print("9. 🔄 Resetar checkpoint de índice")
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
                        cursor.execute('DELETE FROM progresso_efd')
                        cursor.execute('DELETE FROM dependentes_processados')
                        cursor.execute('DELETE FROM planos_processados')
                        cursor.execute('DELETE FROM info_dependentes_processados')
                        conn.commit()
                        conn.close()
                        print("✅ Todos os dados foram limpos!")
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
    
    def exportar_relatorio(self):
        """Exporta relatório para Excel"""
        try:
            conn = self.conectar_banco()
            if not conn:
                return
            
            # Buscar todos os dados
            cursor = conn.cursor()
            
            # Progresso geral
            cursor.execute('''
                SELECT cpf_titular, nome_titular, etapa_atual, status, 
                       timestamp, observacoes
                FROM progresso_efd 
                ORDER BY timestamp DESC
            ''')
            
            progresso_data = cursor.fetchall()
            
            # Dependentes
            cursor.execute('''
                SELECT cpf_titular, cpf_dependente, relacao, descricao_agregado,
                       status, timestamp
                FROM dependentes_processados 
                ORDER BY timestamp DESC
            ''')
            
            dependentes_data = cursor.fetchall()
            
            # Planos
            cursor.execute('''
                SELECT cpf_titular, cnpj_operadora, valor_titular,
                       status, timestamp
                FROM planos_processados 
                ORDER BY timestamp DESC
            ''')
            
            planos_data = cursor.fetchall()
            
            conn.close()
            
            # Criar Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_checkpoint_{timestamp}.xlsx"
            
            with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
                # Aba Progresso
                df_progresso = pd.DataFrame(progresso_data, columns=[
                    'CPF_Titular', 'Nome_Titular', 'Etapa_Atual', 'Status', 
                    'Timestamp', 'Observacoes'
                ])
                df_progresso.to_excel(writer, sheet_name='Progresso', index=False)
                
                # Aba Dependentes
                df_dependentes = pd.DataFrame(dependentes_data, columns=[
                    'CPF_Titular', 'CPF_Dependente', 'Relacao', 'Descricao_Agregado',
                    'Status', 'Timestamp'
                ])
                df_dependentes.to_excel(writer, sheet_name='Dependentes', index=False)
                
                # Aba Planos
                df_planos = pd.DataFrame(planos_data, columns=[
                    'CPF_Titular', 'CNPJ_Operadora', 'Valor_Titular',
                    'Status', 'Timestamp'
                ])
                df_planos.to_excel(writer, sheet_name='Planos', index=False)
            
            print(f"✅ Relatório exportado: {nome_arquivo}")
            
        except Exception as e:
            print(f"❌ Erro ao exportar relatório: {e}")
    
    def resetar_progresso_cpf(self):
        """Reseta o progresso de um CPF específico"""
        try:
            cpf = input("\n🔄 Digite o CPF para resetar: ").strip()
            if not cpf:
                print("❌ CPF não informado")
                return
            
            confirmar = input(f"⚠️ Tem certeza que quer resetar o progresso do CPF {cpf}? (digite 'SIM'): ")
            if confirmar != "SIM":
                print("❌ Operação cancelada")
                return
            
            conn = self.conectar_banco()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Verificar se CPF existe
            cursor.execute('SELECT COUNT(*) FROM progresso_efd WHERE cpf_titular = ?', (cpf,))
            existe = cursor.fetchone()[0]
            
            if existe == 0:
                print(f"❌ CPF {cpf} não encontrado no banco")
                conn.close()
                return
            
            # Limpar dados do CPF
            cursor.execute('DELETE FROM progresso_efd WHERE cpf_titular = ?', (cpf,))
            cursor.execute('DELETE FROM dependentes_processados WHERE cpf_titular = ?', (cpf,))
            cursor.execute('DELETE FROM planos_processados WHERE cpf_titular = ?', (cpf,))
            cursor.execute('DELETE FROM info_dependentes_processados WHERE cpf_titular = ?', (cpf,))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Progresso do CPF {cpf} foi resetado!")
            print("💡 O CPF pode ser processado novamente na próxima execução")
            
        except Exception as e:
            print(f"❌ Erro ao resetar progresso: {e}")
    
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
            
            # Buscar planos processados
            df_planos = pd.read_sql_query('''
                SELECT 
                    cpf_titular,
                    cnpj_operadora,
                    valor_titular,
                    status,
                    timestamp
                FROM planos_processados 
                ORDER BY timestamp DESC
            ''', conn)
            
            # Buscar informações de dependentes
            df_info_dependentes = pd.read_sql_query('''
                SELECT 
                    cpf_titular,
                    cpf_dependente,
                    valor_dependente,
                    status,
                    timestamp
                FROM info_dependentes_processados 
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
                dependentes_sucesso = len(df_dependentes[(df_dependentes['cpf_titular'] == cpf) & (df_dependentes['status'] == 'sucesso')])
                
                # Contar planos
                total_planos = len(df_planos[df_planos['cpf_titular'] == cpf])
                planos_sucesso = len(df_planos[(df_planos['cpf_titular'] == cpf) & (df_planos['status'] == 'sucesso')])
                
                # Contar info dependentes
                total_info = len(df_info_dependentes[df_info_dependentes['cpf_titular'] == cpf])
                info_sucesso = len(df_info_dependentes[(df_info_dependentes['cpf_titular'] == cpf) & (df_info_dependentes['status'] == 'sucesso')])
                
                resumo_cpfs.append({
                    'CPF_Titular': cpf,
                    'Nome_Titular': ultimo_status['nome_titular'],
                    'Status_Final': ultimo_status['status'],
                    'Etapa_Atual': ultimo_status['etapa_atual'],
                    'Total_Dependentes': total_dependentes,
                    'Dependentes_Sucesso': dependentes_sucesso,
                    'Total_Planos': total_planos,
                    'Planos_Sucesso': planos_sucesso,
                    'Total_Info_Dependentes': total_info,
                    'Info_Sucesso': info_sucesso,
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
                
                # Aba Planos
                df_planos.to_excel(writer, sheet_name='Planos', index=False)
                
                # Aba Info Dependentes
                df_info_dependentes.to_excel(writer, sheet_name='Info_Dependentes', index=False)
                
                # Aba Estatísticas
                stats = {
                    'Metrica': [
                        'Total de CPFs',
                        'CPFs com Sucesso',
                        'CPFs Pulados',
                        'CPFs com Erro',
                        'Total de Dependentes',
                        'Total de Planos',
                        'Total de Info Dependentes'
                    ],
                    'Valor': [
                        len(cpfs_unicos),
                        len(df_resumo[df_resumo['Status_Final'] == 'sucesso']),
                        len(df_resumo[df_resumo['Status_Final'] == 'pulado']),
                        len(df_resumo[df_resumo['Status_Final'] == 'erro']),
                        len(df_dependentes),
                        len(df_planos),
                        len(df_info_dependentes)
                    ]
                }
                df_stats = pd.DataFrame(stats)
                df_stats.to_excel(writer, sheet_name='Estatisticas', index=False)
            
            print(f"✅ Planilha gerada: {nome_arquivo}")
            print(f"📊 {len(cpfs_unicos)} CPFs processados")
            print(f"📋 {len(df_resumo)} registros no resumo")
            
        except Exception as e:
            print(f"❌ Erro ao gerar planilha: {e}")
    
    def resetar_checkpoint_indice(self):
        """Reseta o checkpoint de índice para começar do zero"""
        try:
            confirmar = input("⚠️ Tem certeza que quer resetar o checkpoint de índice? (digite 'SIM'): ")
            if confirmar != "SIM":
                print("❌ Operação cancelada")
                return
            
            conn = self.conectar_banco()
            if not conn:
                return
            
            cursor = conn.cursor()
            cursor.execute('DELETE FROM checkpoint_indice')
            conn.commit()
            conn.close()
            
            print("✅ Checkpoint de índice resetado!")
            print("💡 O processamento começará do grupo 1 na próxima execução")
            
        except Exception as e:
            print(f"❌ Erro ao resetar checkpoint de índice: {e}")
    
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
                    self.exportar_relatorio()
                elif opcao == "7":
                    self.resetar_progresso_cpf()
                elif opcao == "8":
                    self.gerar_planilha_visualizacao()
                elif opcao == "9":
                    self.resetar_checkpoint_indice()
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
