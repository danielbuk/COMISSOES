# 📈 Sistema de Ajuste Manual de Faturamento

## Visão Geral

O sistema de ajuste manual de faturamento permite adicionar valores de faturamento (positivos ou negativos) para vendedores específicos, com taxas de comissão próprias e independentes das regras padrão do sistema.

## 🎯 Características Principais

### Integridade dos Dados
- **Dados do Oracle preservados**: O faturamento importado do Oracle NÃO é modificado
- **Cálculos originais mantidos**: A comissão base do Oracle permanece inalterada
- **Camada separada**: O ajuste é uma camada adicional que não interfere nos dados originais

### Funcionalidades
- ✅ Ajuste de faturamento com valor positivo ou negativo
- ✅ Taxa de comissão específica para cada ajuste
- ✅ Campo de motivo/justificativa
- ✅ Interface visual clara e intuitiva
- ✅ Cálculos automáticos e transparentes

## 🏗️ Arquitetura Técnica

### Modelo de Banco de Dados

```sql
CREATE TABLE ajuste_faturamento (
    id INTEGER PRIMARY KEY,
    vendedor_rca INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    valor_ajuste FLOAT NOT NULL,
    taxa_comissao_ajuste FLOAT NOT NULL,
    motivo TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendedor_rca) REFERENCES vendedor(rca),
    UNIQUE(vendedor_rca, mes, ano)
);
```

### Fluxo de Cálculo

1. **Comissão Base Oracle**: Calculada normalmente com faturamento do Oracle
2. **Comissão do Ajuste**: `valor_ajuste × taxa_comissao_ajuste`
3. **Comissão Base Total**: `comissao_base_oracle + comissao_do_ajuste`
4. **Faturamento Final**: `faturamento_oracle + valor_ajuste`
5. **Comissão Final**: Aplica ajustes financeiros sobre a comissão base total

## 🎨 Interface do Usuário

### Botão de Acesso
- Localização: Card de cada vendedor no relatório
- Ícone: 📈 Ajuste de Faturamento
- Cor: Verde (diferenciação visual)

### Modal de Ajuste
- **Valor do Ajuste**: Campo numérico (positivo/negativo)
- **Taxa de Comissão**: Campo percentual (ex: 0.5 para 0,5%)
- **Motivo**: Campo de texto para justificativa

### Exibição no Relatório
```
Faturamento Oracle: R$ 50.000,00
Ajuste Manual: +R$ 5.000,00 (0.5%)
Faturamento Total: R$ 55.000,00

Comissão (vendas Oracle): R$ 750,00
Comissão (ajuste manual): R$ 25,00
Comissão Base Total: R$ 775,00
```

## 🔧 APIs Disponíveis

### GET /api/ajuste-faturamento/{rca}/{ano}/{mes}
Busca ajuste existente para um vendedor/período específico.

**Resposta:**
```json
{
  "success": true,
  "ajuste": {
    "id": 1,
    "vendedor_rca": 123,
    "mes": 12,
    "ano": 2024,
    "valor_ajuste": 5000.00,
    "taxa_comissao_ajuste": 0.005,
    "motivo": "Divisão de vendas",
    "data_criacao": "15/12/2024 10:30",
    "data_atualizacao": "15/12/2024 10:30"
  }
}
```

### POST /api/ajuste-faturamento
Cria ou atualiza ajuste de faturamento.

**Payload:**
```json
{
  "vendedor_rca": 123,
  "mes": 12,
  "ano": 2024,
  "valor_ajuste": 5000.00,
  "taxa_comissao_ajuste": 0.005,
  "motivo": "Divisão de vendas"
}
```

## 📊 Exemplos de Uso

### Cenário 1: Divisão de Vendas
- **Situação**: Vendedor A e B dividiram uma venda de R$ 10.000
- **Ajuste**: +R$ 5.000 para cada vendedor
- **Taxa**: 1,5% (taxa padrão da empresa)
- **Resultado**: Cada vendedor recebe comissão sobre R$ 5.000

### Cenário 2: Correção de Erro
- **Situação**: Venda foi registrada no vendedor errado
- **Ajuste**: -R$ 3.000 (remove do vendedor A)
- **Taxa**: 0% (sem comissão sobre correção)
- **Resultado**: Valor removido sem afetar comissão

### Cenário 3: Comissão Especial
- **Situação**: Venda com comissão diferenciada
- **Ajuste**: +R$ 2.000
- **Taxa**: 2,5% (taxa especial)
- **Resultado**: Comissão adicional com taxa própria

## 🛡️ Validações e Segurança

### Validações do Frontend
- Taxa de comissão entre 0% e 100%
- Valor do ajuste obrigatório
- Motivo recomendado (não obrigatório)

### Validações do Backend
- Vendedor deve existir
- Período válido (mês 1-12, ano > 2000)
- Taxa de comissão entre 0 e 1 (0% a 100%)
- Unicidade por vendedor/período

## 🔄 Atualização do Sistema

### Passos para Implementação
1. ✅ Criar modelo `AjusteFaturamento`
2. ✅ Atualizar função `process_commissions`
3. ✅ Adicionar APIs REST
4. ✅ Implementar interface frontend
5. ✅ Atualizar banco de dados
6. ✅ Testar funcionalidade

### Comandos de Atualização
```bash
# Atualizar banco de dados
python update_database.py

# Executar aplicação
python run.py
```

## 📈 Benefícios

### Para o Negócio
- **Flexibilidade**: Permite regras específicas sem alterar dados originais
- **Rastreabilidade**: Motivo registrado para cada ajuste
- **Transparência**: Cálculos claros e separados
- **Auditoria**: Histórico completo de ajustes

### Para o Usuário
- **Simplicidade**: Interface intuitiva
- **Visibilidade**: Valores claramente separados
- **Controle**: Taxa de comissão específica
- **Documentação**: Motivo obrigatório

## 🚀 Próximas Melhorias

### Funcionalidades Futuras
- [ ] Histórico de ajustes por vendedor
- [ ] Relatório específico de ajustes
- [ ] Aprovação de ajustes por gestor
- [ ] Exportação de dados de ajustes
- [ ] Dashboard de métricas de ajustes

### Melhorias Técnicas
- [ ] Cache de ajustes para performance
- [ ] Validação de limites por vendedor
- [ ] Integração com sistema de aprovações
- [ ] Backup automático de ajustes

## 📞 Suporte

Para dúvidas ou problemas com a funcionalidade de ajuste de faturamento:

1. Verifique se o banco de dados foi atualizado
2. Confirme se as APIs estão respondendo
3. Teste com valores pequenos primeiro
4. Consulte os logs da aplicação

---

**Versão**: 1.0  
**Data**: Dezembro 2024  
**Autor**: Sistema de Comissões
