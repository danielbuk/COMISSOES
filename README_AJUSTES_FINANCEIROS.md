# Funcionalidade de Ajustes Financeiros Manuais

## Visão Geral

Esta funcionalidade permite que a equipe financeira insira e ajuste manualmente três valores específicos para cada vendedor em cada período (mês/ano):

1. **Valor Título em Aberto** - Diminui da comissão
2. **Valor Ret. Merc. (Devolução)** - Diminui da comissão
3. **Valor Acrésc. Título Pago Mês Ant.** - Soma à comissão

Esses valores são aplicados como ajustes financeiros universais para cada vendedor, calculando a comissão final através da fórmula:

**Comissão Final = Comissão Base + Valor Acrésc. Título Pago Mês Ant. - Valor Ret. Merc. - Valor Título Aberto**

## Como Usar

### 1. Acessando a Funcionalidade

1. Acesse o relatório de comissões para o período desejado
2. Para cada vendedor, você verá um botão **"✏️ Ajustes Financeiros"** no cabeçalho do card
3. Clique no botão para abrir o modal de edição

### 2. Editando os Valores

1. **Modal de Ajustes**: Um pop-up aparecerá com o título "Ajustes Financeiros para [Nome do Vendedor] - [Mês]/[Ano]"

2. **Campos Disponíveis**:
   - **Valor Título em Aberto**: Digite o valor manual
   - **Valor Ret. Merc. (Devolução)**: Digite o valor manual
   - **Valor Acrésc. Título Pago Mês Ant.**: Digite o valor manual

3. **Salvando**:
   - Clique em **"Salvar Ajustes"** para salvar as alterações
   - Clique em **"Cancelar"** para fechar sem salvar

### 3. Visualizando os Resultados

- Após salvar, a página será recarregada automaticamente
- Os ajustes financeiros aparecem em uma seção dedicada no final de cada card de vendedor
- A comissão final é calculada automaticamente aplicando os ajustes
- Se nenhum ajuste manual foi feito, os valores serão exibidos como R$ 0,00

## Funcionalidades Técnicas

### Backend

#### Nova Tabela no Banco de Dados
- **Tabela**: `ajuste_financeiro`
- **Campos**:
  - `id` (chave primária)
  - `vendedor_rca` (chave estrangeira para vendedor)
  - `mes` (mês do ajuste)
  - `ano` (ano do ajuste)
  - `valor_titulo_aberto` (valor manual)
  - `valor_ret_merc` (valor manual)
  - `valor_acresc_titulo_pago_mes_ant` (valor manual)
  - `data_criacao` (data de criação)
  - `data_atualizacao` (data da última atualização)

#### Novas APIs
- **GET** `/api/ajuste-financeiro/<rca>/<ano>/<mes>`: Busca ajustes de um vendedor em um período
- **POST** `/api/ajuste-financeiro`: Cria ou atualiza ajustes

### Frontend

#### Interface
- Botão de edição em cada card de vendedor
- Modal responsivo com formulário
- Validação de campos obrigatórios
- Feedback visual de sucesso/erro

#### JavaScript
- Carregamento automático de valores existentes
- Submissão assíncrona via AJAX
- Recarregamento automático da página após salvar

## Comportamento do Sistema

### Antes da Implementação
- Os valores eram lidos diretamente do Oracle
- Não havia possibilidade de ajuste manual
- Dados eram sempre os mesmos que vinham do sistema

### Após a Implementação
- Os valores são inseridos manualmente pela equipe financeira
- Se não houver ajuste manual, os valores são exibidos como R$ 0,00
- Os valores manuais são aplicados como ajustes universais para cada vendedor
- A comissão final é calculada automaticamente aplicando os ajustes
- Cada vendedor pode ter valores diferentes para cada período

## Vantagens

1. **Flexibilidade**: Permite ajustes específicos por vendedor e período
2. **Controle**: Equipe financeira tem controle total sobre os valores
3. **Rastreabilidade**: Mantém histórico de criação e atualização
4. **Interface Intuitiva**: Fácil de usar, sem necessidade de conhecimento técnico
5. **Integração**: Funciona perfeitamente com o sistema existente

## Considerações Importantes

- Os ajustes são salvos por vendedor e período específico
- Não há limite de valores (podem ser positivos ou negativos)
- Os valores são mantidos mesmo após novas importações do Oracle
- A funcionalidade não afeta outros aspectos do relatório (faturamento, comissões base, etc.)
- Os ajustes financeiros aparecem em uma seção dedicada no final de cada card
- A comissão final é destacada visualmente para facilitar a visualização

## Suporte

Para dúvidas ou problemas com esta funcionalidade, entre em contato com a equipe de desenvolvimento.
