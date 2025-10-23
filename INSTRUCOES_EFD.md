# 🏛️ Sistema EFD-REINF - Instruções de Uso

## 📋 Visão Geral

Criei um sistema completo que simula o formulário EFD-REINF com todas as funcionalidades que você descreveu:

### ✨ Funcionalidades Implementadas

1. **Menu Principal** - Página inicial com navegação
2. **Formulário Multi-etapas** - Exatamente como você descreveu:
   - **Etapa 1**: Data, CNPJ e CPF + botão Continuar
   - **Etapa 2**: Botões para adicionar dependentes e plano de saúde
   - **Etapa 3**: Resumo e envio da declaração

3. **Sistema de Dependentes**:
   - Modal para adicionar CPF e relação de dependência
   - Lista dinâmica de dependentes adicionados
   - Opção de remover dependentes

4. **Sistema de Plano de Saúde**:
   - Modal para CNPJ do plano e valor pago
   - Lista dinâmica de planos adicionados
   - Desbloqueia botão para informações dos dependentes

5. **Informações dos Dependentes**:
   - Select com CPFs dos dependentes cadastrados
   - Campo de valor para cada dependente
   - Só aparece após adicionar pelo menos um plano

6. **Páginas de Suporte**:
   - Página de sucesso com protocolo
   - Visualização de todas as declarações
   - Estilo visual similar ao EFD-REINF

## 🚀 Como Executar

### 1. Iniciar o Servidor
```bash
cd /home/lipelou/Documentos/form
source venv/bin/activate
python app.py
```

### 2. Acessar o Sistema
- **Menu Principal**: http://localhost:5000
- **Formulário EFD-REINF**: http://localhost:5000/formulario
- **Visualizar Declarações**: http://localhost:5000/visualizar_efd

### 3. Executar Testes de Automação

#### Teste Original (Desenvolvedores)
```bash
python test.py
```

#### Teste EFD-REINF (Novo)
```bash
python test_efd.py
```

## 🎯 Fluxo do Teste EFD-REINF

O teste `test_efd.py` executa exatamente o fluxo que você descreveu:

1. **Acessa o menu** → Clica em "Acessar Formulário"
2. **Preenche dados iniciais** → Data, CNPJ, CPF
3. **Clica em Continuar** → Vai para próxima etapa
4. **Adiciona dependente** → CPF + relação de dependência
5. **Adiciona plano de saúde** → CNPJ + valor pago
6. **Adiciona informações do dependente** → Select CPF + valor
7. **Finaliza e envia** → Resumo + envio da declaração

## 📊 Estrutura do Banco de Dados

### Tabela Original (Desenvolvedores)
```sql
cadastros (id, nome, sobrenome, email, lado_dev, senioridade, tecnologias, experiencia, data_cadastro)
```

### Nova Tabela (EFD-REINF)
```sql
efd_declaracoes (id, data, cnpj, cpf, dependentes, planos_saude, dependentes_planos, data_cadastro)
```

## 🎨 Características Visuais

- **Cores**: Azul oficial (#1e3c72) similar ao EFD-REINF
- **Layout**: Formulário multi-etapas com modais
- **Responsivo**: Funciona em diferentes tamanhos de tela
- **UX**: Navegação intuitiva com feedback visual

## 🔧 Arquivos Criados/Modificados

### Novos Arquivos:
- `templates/menu.html` - Menu principal
- `templates/formulario_efd.html` - Formulário EFD-REINF
- `templates/sucesso_efd.html` - Página de sucesso
- `templates/visualizar_efd.html` - Visualização de declarações
- `test_efd.py` - Teste de automação EFD-REINF
- `INSTRUCOES_EFD.md` - Este arquivo

### Arquivos Modificados:
- `app.py` - Adicionadas rotas e tabela EFD-REINF

## 🧪 Testando a Automação

O teste Selenium simula um usuário real:

1. **Navegação**: Menu → Formulário
2. **Preenchimento**: Todos os campos obrigatórios
3. **Interação**: Modais, selects, botões
4. **Validação**: Verifica se chegou na página de sucesso
5. **Screenshot**: Em caso de erro, salva imagem

## 🎯 Próximos Passos

Agora você pode:

1. **Executar os testes** para verificar se tudo funciona
2. **Personalizar** os campos conforme necessário
3. **Adicionar validações** específicas do EFD-REINF
4. **Expandir** com mais funcionalidades

## 🆘 Solução de Problemas

### Erro de Chrome/Chromium:
```bash
# Instalar Chromium se necessário
sudo apt update
sudo apt install chromium-browser
```

### Erro de Dependências:
```bash
pip install -r requirements.txt
```

### Erro de Porta:
```bash
# Verificar se porta 5000 está livre
lsof -i :5000
```

---

**🎉 Sistema pronto para uso! Execute `python test_efd.py` para testar a automação completa.**
