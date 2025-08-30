# Sistema de Comissões Flask

Aplicação web completa em Flask para calcular comissões de vendas, substituindo um script Google Apps Script existente.

## Características

- **Backend:** Python 3.10+ com Flask
- **Banco de Dados (Regras):** SQLite com Flask-SQLAlchemy
- **Banco de Dados (Fonte):** Oracle
- **Interface:** Web responsiva com relatórios detalhados
- **Cache Local:** Sistema de cache para evitar consultas desnecessárias ao Oracle
- **Seleção de Período:** Interface para selecionar mês/ano específico

## Instalação

1. **Clone o repositório e navegue até o diretório:**
   ```bash
   cd sistema-comissoes-flask
   ```

2. **Crie um ambiente virtual Python:**
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure as credenciais (opcional):**
   Crie um arquivo `.env` na raiz do projeto com suas credenciais:
   ```ini
   ORACLE_USER="seu_usuario"
   ORACLE_PASSWORD="sua_senha"
   ORACLE_DSN="seu_servidor:porta/banco"
   DATABASE_URL="sqlite:///business_rules.db"
   ```

6. **Popule o banco de dados de regras:**
   ```bash
   python seed_database.py
   ```

7. **Execute a aplicação:**
   ```bash
   python run.py
   ```

8. **Acesse no navegador:**
   ```
   http://127.0.0.1:5000
   ```

## Como Usar

### 1. Página Inicial
- Acesse `http://127.0.0.1:5000`
- Selecione o mês e ano desejados
- Clique em "Gerar Relatório" para ver dados já importados
- Clique em "Importar do Oracle" para buscar novos dados

### 2. Importação de Dados
- Selecione o mês/ano desejado
- Clique em "Importar do Oracle"
- Confirme a importação no modal
- Os dados serão salvos localmente no cache

### 3. Visualização de Relatórios
- Após importar, os dados ficam disponíveis para consulta rápida
- Acesse relatórios de meses já importados sem consultar o Oracle
- Visualize comissões detalhadas por vendedor

## Estrutura do Projeto

```
/sistema-comissoes-flask
|
|-- app/
|   |-- __init__.py         # Inicialização do app Flask
|   |-- models.py           # Modelos SQLAlchemy
|   |-- services.py         # Lógica de negócio
|   |-- routes.py           # Rotas da aplicação
|   |-- templates/
|   |   |-- base.html       # Template base
|   |   |-- index.html      # Página inicial
|   |   `-- relatorio.html  # Template do relatório
|   `-- static/
|       `-- styles.css      # Estilos CSS
|
|-- config.py               # Configurações
|-- run.py                  # Ponto de entrada
|-- seed_database.py        # Script de população do BD
|-- requirements.txt        # Dependências
`-- README.md              # Este arquivo
```

## Funcionalidades

- **Conexão com Oracle:** Busca dados de vendas diretamente do banco Oracle
- **Cache Local:** Armazena dados importados para consulta rápida
- **Seleção de Período:** Interface para escolher mês/ano específico
- **Regras Flexíveis:** Sistema de regras de comissão configurável via banco SQLite
- **Relatórios Detalhados:** Exibição organizada por vendedor com produtos especiais
- **Cálculos Automáticos:** Comissões, devoluções e ajustes financeiros
- **Interface Responsiva:** Design moderno e adaptável a diferentes dispositivos

## Vantagens do Sistema

### Performance
- **Cache Local:** Dados importados ficam salvos localmente
- **Consultas Rápidas:** Relatórios de meses já importados são instantâneos
- **Redução de Carga:** Oracle só é consultado quando necessário

### Flexibilidade
- **Seleção de Período:** Escolha qualquer mês/ano para análise
- **Importação Sob Demanda:** Importe apenas os meses que precisa
- **Regras Configuráveis:** Modifique regras de comissão sem alterar código

### Usabilidade
- **Interface Intuitiva:** Fácil seleção de período e importação
- **Feedback Visual:** Status de importação e mensagens claras
- **Navegação Simples:** Acesso rápido a relatórios já gerados

## Regras de Comissão

O sistema suporta diferentes tipos de regras:
- **Por Vendedor:** Taxa específica para um vendedor
- **Por Produto:** Taxa específica para um produto
- **Vendedor + Produto:** Taxa específica para combinação
- **Taxas Padrão:** Fallback para casos não especificados

### Regras Implementadas
- Taxa especial para Carlos Eduardo (RCA 33): 0.5%
- Produtos Pepsico para Michelle (RCA 83): 2%
- Produtos específicos (hambúrguer): 1%
- Vendedores 1 e 2: 2%
- Taxa padrão: 1.5%

## Suporte

Para dúvidas ou problemas, consulte a documentação ou entre em contato com a equipe de desenvolvimento.
